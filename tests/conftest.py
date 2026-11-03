import copy
import json
from pathlib import Path
import pytest
from gltest.direct import VMContext, create_address, deploy_contract

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def docs():
    return {name: json.loads((ROOT / 'examples' / (name + '.json')).read_text())
            for name in ['order', 'delivery', 'invoice']}


def review(docs, finding='SAME'):
    by_role = {key: {line['id']: line for line in value['lines']} for key, value in docs.items()}
    return {'checks': [
        {'id': line['id'], 'finding': finding,
         'order_quote': by_role['order'][line['id']]['description'],
         'delivery_quote': by_role['delivery'][line['id']]['description'],
         'invoice_quote': line['description'],
         'reason': 'The quoted material, grade and dimensions support this classification.'}
        for line in sorted(docs['invoice']['lines'], key=lambda item: item['id'])]}

@pytest.fixture
def env():
    vm = VMContext()
    buyer, supplier, stranger = [create_address(seed) for seed in ['buyer', 'supplier', 'stranger']]
    vm.sender = buyer
    with vm.activate():
        from gltest.direct.sdk_loader import setup_sdk_paths
        setup_sdk_paths(ROOT / 'contracts/invoice_match_seal.py', version='v0.2.16')
        from genlayer import Address
        buyer, supplier, stranger = [Address(a) if isinstance(a, bytes) else a for a in [buyer, supplier, stranger]]
        vm.sender = buyer
        contract = deploy_contract(ROOT / 'contracts/invoice_match_seal.py', vm, supplier,
                                   sdk_version='v0.2.16')
        yield vm, contract, buyer, supplier, stranger


def prepare(env, docs, finding='SAME'):
    vm, c, buyer, supplier, _ = env
    with vm.prank(buyer):
        c.lock_order(json.dumps(docs['order']))
    order_hash = json.loads(c.get_documents())['order']['canonical_sha256']
    with vm.prank(supplier):
        c.accept_order(order_hash)
        c.submit_invoice(json.dumps(docs['invoice']))
    with vm.prank(buyer):
        c.lock_delivery(json.dumps(docs['delivery']))
    vm.mock_llm('InvoiceMatchSeal', json.dumps(review(docs, finding)))
    return c
