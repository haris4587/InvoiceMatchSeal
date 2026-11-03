"""Read-only verification of source, finality, public views and receipt chain on Studio."""
import argparse
import base64
import hashlib
import json
import time
from pathlib import Path
from genlayer_py import create_account, create_client, studionet
from genlayer_py.types import TransactionHashVariant
from genlayer_py.types.transactions import TRANSACTION_STATUS_NUMBER_TO_NAME
from live_support import transaction_snapshot
from verify_receipt import verify

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('proof', nargs='?', type=Path, default=ROOT / 'docs/live-demo.json')
args = parser.parse_args()
bundle = json.loads(args.proof.read_text())
client = create_client(chain=studionet, account=create_account())
source = (ROOT / 'contracts/invoice_match_seal.py').read_bytes()
assert bundle['source_sha256'] == hashlib.sha256(source).hexdigest(), 'Local source changed'
assert int(client.provider.make_request('eth_chainId', [])['result'], 16) == bundle['chain_id'] == 61999
for entry in bundle['transactions']:
    for attempt in range(60):
        tx = client.get_transaction(entry['tx_hash'])
        status = TRANSACTION_STATUS_NUMBER_TO_NAME[str(tx['status'])].value
        if status == 'FINALIZED':
            break
        if status not in ['ACCEPTED', 'READY_TO_FINALIZE']:
            raise RuntimeError(entry['method'] + ' is not accepted: ' + status)
        print(entry['method'], status, 'waiting for finality', flush=True)
        time.sleep(2)
    else:
        raise TimeoutError('Finality not observed')
    assert not tx.get('leader_only'), 'Leader-only proof is not allowed'
    receipts = tx['consensus_data']['leader_receipt']
    if isinstance(receipts, dict): receipts = [receipts]
    assert receipts and all(r['execution_result'] == 'SUCCESS' for r in receipts), 'VM error'
    assert any(r.get('vote') == 'agree' for r in tx['consensus_data']['validators']), 'No agreeing validator'
    entry['transaction'] = transaction_snapshot(tx)
    print(entry['method'], status, 'VM SUCCESS', flush=True)
# Independently retrieve deployment input, not the source copied into a local bundle.
raw = client.provider.make_request('eth_getTransactionByHash', [bundle['transactions'][0]['tx_hash']])['result']
deployed_source = base64.b64decode(raw['data']['contract_code'])
assert deployed_source == source, 'Deployed source differs from repository contract'
address = bundle['contract_address']

def read(method, args=None):
    value = client.read_contract(address=address, function_name=method, args=args or [],
                                 transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    return json.loads(value)

bundle['receipt'] = read('get_receipt')
bundle['contract_status'] = read('get_status')
bundle['events'] = [read('get_event', [i]) for i in range(1, bundle['contract_status']['event_count'] + 1)]
head = bundle['contract_status']['event_head']
assert verify(bundle, head) == head
expected = 'DISCREPANCY' if bundle.get('case') == 'substitution' else 'MATCHED'
assert bundle['receipt']['outcome'] == expected
assert not bundle['receipt']['arithmetic']['findings'], 'Semantic demonstration must have matching arithmetic'
assert bundle['receipt']['reason'] == 'INDEPENDENT_SEMANTIC_CONSENSUS'
bundle['status'] = 'FINALIZED_LIFECYCLE_VERIFIED'
bundle['verification'] = {'deployed_source_matches': True, 'all_transactions_finalized': True,
                          'all_vm_executions_successful': True, 'agreeing_validators_observed': True,
                          'finalized_state_read': True, 'event_chain_verified': True, 'trusted_head': head}
bundle.pop('error', None)
args.proof.write_text(json.dumps(bundle, indent=2) + '\n')
print('Verified finalized source-bound receipt:', expected, address, head, flush=True)
