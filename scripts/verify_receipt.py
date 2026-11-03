"""Offline verification of an exported event chain. Anchor expected_head on-chain.
A valid hash proves internal consistency, not document truth or network consensus.
"""
import argparse
import hashlib
import json
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def check(ok, message):
    if not ok:
        raise ValueError(message)


def verify(bundle, expected_head=None):
    events = bundle['events']
    check(bool(events), 'Empty history')
    previous = '0' * 64
    domain = events[0]['domain']
    documents = {}
    last_receipt = None
    accepted = False
    attempts = 0
    sealed = False
    for sequence, original in enumerate(events, 1):
        event = dict(original)
        event_hash = event.pop('event_hash')
        check(event['domain'] == domain, 'Domain changed')
        check(event['sequence'] == sequence, 'Nonconsecutive sequence')
        check(event['previous_hash'] == previous, 'Broken chain')
        check(event_hash == digest(event), 'Event hash mismatch')
        check(event['actor'] in [domain['buyer'], domain['supplier']], 'Unknown actor')
        payload, kind = event['payload'], event['kind']
        roles = {'ORDER_LOCKED': ('order', 'buyer'), 'DELIVERY_LOCKED': ('delivery', 'buyer'),
                 'INVOICE_LOCKED': ('invoice', 'supplier')}
        if kind in roles:
            name, actor_role = roles[kind]
            check(event['actor'] == domain[actor_role], 'Wrong document actor')
            check(name not in documents, 'Document overwritten')
            check(name == 'order' or accepted, 'Document precedes acceptance')
            check(payload['canonical_sha256'] == digest(payload['data']), 'Document hash mismatch')
            documents[name] = payload
        elif kind == 'ORDER_ACCEPTED':
            check('order' in documents and not accepted, 'Invalid acceptance order')
            check(event['actor'] == domain['supplier'], 'Wrong acceptance actor')
            check(payload['canonical_sha256'] == documents['order']['canonical_sha256'],
                  'Accepted different order')
            accepted = True
        elif kind == 'RECONCILED':
            check(set(documents) == {'order', 'delivery', 'invoice'}, 'Missing documents')
            check(not sealed, 'Review after seal')
            receipt = dict(payload)
            decision_hash = receipt.pop('decision_hash')
            check(decision_hash == digest(receipt), 'Decision hash mismatch')
            check(receipt['domain'] == domain and receipt['policy'] == domain['policy'], 'Wrong receipt domain')
            check(receipt['previous_event_hash'] == previous, 'Wrong receipt predecessor')
            attempts += 1
            check(receipt['attempt'] == attempts and attempts <= 3, 'Invalid attempt')
            check(receipt['payment_authorized'] is False, 'Payment authority prohibited')
            for name, doc in documents.items():
                check(receipt[name + '_sha256'] == doc['canonical_sha256'], 'Receipt evidence mismatch')
            check(receipt['outcome'] in ['MATCHED', 'PARTIAL_MATCH', 'DISCREPANCY', 'INCONCLUSIVE'],
                  'Invalid outcome')
            sealed = receipt['outcome'] != 'INCONCLUSIVE' or attempts == 3
            check(receipt['sealed'] == sealed, 'Incorrect seal state')
            last_receipt = payload
        else:
            raise ValueError('Unknown event type')
        previous = event_hash
    check(last_receipt is not None and bundle['receipt'] == last_receipt, 'Latest receipt mismatch')
    status = bundle['contract_status']
    check(status['event_count'] == len(events) and status['event_head'] == previous, 'State head mismatch')
    check(status['domain'] == domain and status['attempts'] == attempts and status['sealed'] == sealed,
          'State summary mismatch')
    if expected_head is not None:
        check(previous == expected_head, 'Trusted on-chain head mismatch')
    return previous


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--expected-head', help='Trusted get_status().event_head from the deployed contract')
    args = parser.parse_args()
    result = verify(json.loads(args.bundle.read_text()), args.expected_head)
    print('Verified event chain and receipt:', result)
