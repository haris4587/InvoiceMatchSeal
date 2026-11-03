import copy
import importlib.util
import json
from pathlib import Path
import pytest
from conftest import prepare
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verifier', ROOT / 'scripts/verify_receipt.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def bundle_for(env, docs):
    c = prepare(env, docs)
    c.evaluate()
    return {'receipt': json.loads(c.get_receipt()), 'contract_status': json.loads(c.get_status()),
            'events': [json.loads(c.get_event(i)) for i in range(1, 6)]}


def test_verifier_accepts_anchored_chain(env, docs):
    bundle = bundle_for(env, docs)
    head = bundle['contract_status']['event_head']
    assert verifier.verify(bundle, head) == head


@pytest.mark.parametrize('attack', ['text', 'decision', 'remove', 'reorder', 'head', 'domain', 'trusted_head'])
def test_verifier_detects_tampering(env, docs, attack):
    b = bundle_for(env, docs)
    trusted_head = b['contract_status']['event_head']
    if attack == 'text': b['events'][0]['payload']['data']['lines'][0]['description'] = 'Fake replacement'
    if attack == 'decision': b['receipt']['outcome'] = 'DISCREPANCY'
    if attack == 'remove': b['events'].pop(1)
    if attack == 'reorder': b['events'][0], b['events'][1] = b['events'][1], b['events'][0]
    if attack == 'head': b['contract_status']['event_head'] = '0' * 64
    if attack == 'domain': b['events'][-1]['domain']['contract'] = '0x' + '0' * 40
    if attack == 'trusted_head': trusted_head = '0' * 64
    with pytest.raises(ValueError): verifier.verify(b, trusted_head)
