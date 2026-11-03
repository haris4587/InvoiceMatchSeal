"""Real hosted Studio lifecycle; NEVER uses leader-only mode or mocked AI.
Uses two generated demo wallets; private keys remain in ignored .private/.
Not intended for mainnet or monetary value. Run from any working directory.
"""
import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from live_support import transaction_snapshot
from genlayer_py import create_account, create_client, studionet
from genlayer_py.types import CalldataAddress
from genlayer_py.types.transactions import TRANSACTION_STATUS_NUMBER_TO_NAME

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--case', choices=['matched', 'substitution'], default='matched')
case = parser.parse_args().case
fixture = {name: json.loads((ROOT / 'examples' / (name + '.json')).read_text())
           for name in ['order', 'delivery', 'invoice']}
if case == 'substitution':
    fixture['delivery']['lines'][0]['description'] = 'Received white 100 percent polyester bath towels, 500 gsm, size 70 x 140 cm. Cotton towels were not delivered.'
expected_outcome = 'MATCHED' if case == 'matched' else 'DISCREPANCY'
PRIVATE = ROOT / '.private'
PRIVATE.mkdir(exist_ok=True, mode=0o700)
keyfile = PRIVATE / 'demo-wallets.json'
if not keyfile.exists():
    wallets = {role: create_account().key.hex() for role in ['buyer', 'supplier']}
    fd = os.open(keyfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(wallets, f)
wallets = json.loads(keyfile.read_text())
accounts = {role: create_account(key) for role, key in wallets.items()}
client = create_client(chain=studionet, account=accounts['buyer'])
code = (ROOT / 'contracts/invoice_match_seal.py').read_bytes()
outfile = ROOT / ('docs/live-demo.json' if case == 'matched' else 'docs/live-substitution.json')
record = {'network': 'studionet', 'rpc': 'https://studio.genlayer.com/api', 'chain_id': 61999,
          'source_sha256': hashlib.sha256(code).hexdigest(), 'leader_only': False,
          'mocked_ai': False, 'case': case, 'wallets': {role: a.address for role, a in accounts.items()},
          'transactions': [], 'status': 'STARTED'}

if outfile.exists():
    previous_record = json.loads(outfile.read_text())
    if (previous_record.get('source_sha256') == record['source_sha256'] and
            previous_record.get('wallets') == record['wallets']):
        record = previous_record

def save():
    for entry in record['transactions']:
        if 'transaction' in entry:
            entry['transaction'] = transaction_snapshot(entry['transaction'])
    outfile.write_text(json.dumps(record, indent=2, default=str) + '\n')


def wait(tx):
    # Poll in short increments so progress is visible; bounded total duration.
    last = None
    for _ in range(120):
        data = client.get_transaction(tx)
        status = str(data.get('status'))
        if status in TRANSACTION_STATUS_NUMBER_TO_NAME:
            status = TRANSACTION_STATUS_NUMBER_TO_NAME[status].value
        if status != last:
            print('  status:', status, flush=True)
            last = status
        if status in ['ACCEPTED', 'FINALIZED']:
            return data
        if status in ['CANCELED', 'UNDETERMINED', 'LEADER_TIMEOUT', 'VALIDATORS_TIMEOUT']:
            raise RuntimeError('Transaction did not succeed: ' + status)
        time.sleep(2)
    raise TimeoutError('Transaction did not reach accepted status')


def transact(method, role='buyer', args=None, deploy=False):
    print('Sending', method, flush=True)
    previous_entry = next((entry for entry in record['transactions'] if entry['method'] == method), None)
    if previous_entry:
        tx = previous_entry['tx_hash']
    elif deploy:
        tx = client.deploy_contract(code=code, args=[CalldataAddress(accounts['supplier'].address)],
                                    account=accounts[role], leader_only=False)
    else:
        tx = client.write_contract(address=record['contract_address'], function_name=method,
                                   account=accounts[role], args=args or [], leader_only=False)
    entry = {'method': method, 'sender': accounts[role].address, 'tx_hash': tx}
    if previous_entry:
        entry = previous_entry
    else:
        record['transactions'].append(entry)
    save()
    data = wait(tx)
    entry['transaction'] = data
    save()
    # ACCEPTED can still contain an execution error: require successful VM output.
    receipts = data.get('consensus_data', {}).get('leader_receipt', [])
    if isinstance(receipts, dict):
        receipts = [receipts]
    if not receipts or any(r.get('execution_result') != 'SUCCESS' for r in receipts):
        raise RuntimeError('VM execution did not succeed for all returned receipts')
    return data


try:
    actual = client.provider.make_request('eth_chainId', [])['result']
    if int(actual, 16) != 61999:
        raise RuntimeError('Wrong chain')
    for role, account in accounts.items():
        balance = client.get_balance(account.address)
        print(role, account.address, 'test balance', balance, flush=True)
        # Hosted Studio exposes test funding; no real funds are requested or transferred.
        if balance == 0:
            client.fund_account(account.address, 10**20)
    data = transact('deploy', deploy=True)
    print('Deploy receipt keys:', list(data), flush=True)
    address = data.get('data', {}).get('contract_address') or data.get('contract_address') or data.get('to_address')
    if not address:
        raise RuntimeError('Missing deployed contract address in receipt')
    record['contract_address'] = address
    save()
    transact('lock_order', args=[json.dumps(fixture['order'])])
    docs = json.loads(client.read_contract(address=address, function_name='get_documents'))
    transact('accept_order', role='supplier', args=[docs['order']['canonical_sha256']])
    transact('lock_delivery', args=[json.dumps(fixture['delivery'])])
    transact('submit_invoice', role='supplier', args=[json.dumps(fixture['invoice'])])
    transact('evaluate')
    record['receipt'] = json.loads(client.read_contract(address=address, function_name='get_receipt'))
    record['contract_status'] = json.loads(client.read_contract(address=address, function_name='get_status'))
    record['events'] = [json.loads(client.read_contract(address=address, function_name='get_event', args=[i]))
                        for i in range(1, record['contract_status']['event_count'] + 1)]
    if record['receipt']['outcome'] != expected_outcome:
        raise RuntimeError('Unexpected outcome: ' + record['receipt']['outcome'])
    record.pop('error', None)
    record['case'] = case
    record['status'] = 'ACCEPTED_LIFECYCLE_VERIFIED'
    save()
    print('Live contract:', address, flush=True)
except Exception as exc:
    record['status'] = 'FAILED'
    record['error'] = type(exc).__name__ + ': ' + str(exc)
    save()
    raise
