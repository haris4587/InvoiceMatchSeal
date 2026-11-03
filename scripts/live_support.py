"""Compact public proof snapshots; transaction hashes allow independent RPC retrieval."""
def execution_snapshot(receipt):
    keys = ['mode', 'vote', 'execution_result', 'result', 'genvm_result', 'nondet_disagree',
            'contract_state_hash', 'eq_outputs']
    out = {key: receipt[key] for key in keys if key in receipt}
    node = receipt.get('node_config', {})
    out['validator_address'] = receipt.get('validator_address') or node.get('address')
    return out


def transaction_snapshot(data):
    keys = ['hash', 'status', 'status_name', 'from_address', 'to_address', 'leader_only',
            'execution_mode', 'num_of_initial_validators', 'result_name']
    out = {key: data[key] for key in keys if key in data}
    consensus = data.get('consensus_data', {})
    leaders = consensus.get('leader_receipt', [])
    if isinstance(leaders, dict):
        leaders = [leaders]
    validators = consensus.get('validators', [])
    out['consensus_data'] = {'votes': consensus.get('votes', {}),
                             'leader_receipt': [execution_snapshot(r) for r in leaders],
                             'validators': [execution_snapshot(r) for r in validators if isinstance(r, dict)]}
    return out
