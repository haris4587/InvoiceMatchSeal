"""Deterministic direct-mode demo with explicitly MOCKED AI; not live consensus evidence."""
import json
import sys
from pathlib import Path
from gltest.direct import VMContext, create_address, deploy_contract
from gltest.direct.sdk_loader import setup_sdk_paths
from verify_receipt import verify
ROOT = Path(__file__).resolve().parents[1]
vm = VMContext()
with vm.activate():
    setup_sdk_paths(ROOT / 'contracts/invoice_match_seal.py', version='v0.2.16')
    buyer, supplier = create_address('offline-buyer'), create_address('offline-supplier')
    vm.sender = buyer
    c = deploy_contract(ROOT / 'contracts/invoice_match_seal.py', vm, supplier, sdk_version='v0.2.16')
    docs = {name: json.loads((ROOT / 'examples' / (name + '.json')).read_text())
            for name in ['order', 'delivery', 'invoice']}
    c.lock_order(json.dumps(docs['order']))
    with vm.prank(supplier):
        c.accept_order(json.loads(c.get_documents())['order']['canonical_sha256'])
        c.submit_invoice(json.dumps(docs['invoice']))
    c.lock_delivery(json.dumps(docs['delivery']))
    check = {'id': 'TOWEL', 'finding': 'SAME',
             **{name + '_quote': docs[name]['lines'][0]['description'] for name in docs},
             'reason': 'Mocked fixture: all descriptions identify cotton towels of the same grade and size.'}
    vm.mock_llm('InvoiceMatchSeal', json.dumps({'checks': [check]}))
    c.evaluate()
    if not vm.run_validator():
        raise RuntimeError('Mocked independent validator failed')
    bundle = {'mode': 'DIRECT_MODE_MOCKED_AI', 'receipt': json.loads(c.get_receipt()),
              'contract_status': json.loads(c.get_status()),
              'events': [json.loads(c.get_event(n)) for n in range(1, 6)]}
    verify(bundle, bundle['contract_status']['event_head'])
    path = ROOT / 'examples/offline-receipt.json'
    path.write_text(json.dumps(bundle, indent=2) + '\n')
    print('MOCKED demo outcome:', bundle['receipt']['outcome'])
    print('Receipt verified:', path)
