# Deployment and reviewer workflow

## Reproduce

```bash
python -m pip install -r requirements-dev.txt
pytest
python scripts/offline_demo.py
genvm-lint check contracts/invoice_match_seal.py
genvm-lint typecheck contracts/invoice_match_seal.py
```

The first SDK download may take a few minutes. The deployable artifact is the single contract Python file. Its first-line dependency pins the runtime. `docs/abi.json` is SDK-extracted.

## Hosted Studio

```bash
python scripts/live_demo.py
python scripts/verify_receipt.py docs/live-demo.json --expected-head ACTUAL_ON_CHAIN_HEAD
```

This script explicitly targets `https://studio.genlayer.com/api`, chain 61999. It creates two demo wallets in ignored `.private/demo-wallets.json`, checks the chain, obtains hosted Studio test funds if needed and deploys with normal validator consensus (`leader_only=False`). It locks the synthetic order, accepts it with the supplier wallet, locks delivery/invoice, evaluates with real AI, and exports transactions, state and the event chain. No mocked responses are used. Keys stay local and must never be committed or used for valuable assets.

Rerunning resumes recorded transaction hashes when the source hash and wallets match. To deliberately start a new instance, archive the old evidence file before rerunning. The script requires successful VM execution; an accepted transaction containing a contract error is not treated as success. Exact address, source hash, transaction hashes and observed status are in `live-demo.json` and summarized in `LIVE.md`. Studio is a sandbox and may reset. A Studio result is not a Bradbury or production deployment.

## Your own wallet

```bash
genlayer network set studionet
genlayer network info
genlayer deploy --contract contracts/invoice_match_seal.py --args SUPPLIER_WALLET_ADDRESS
```

Use distinct buyer and supplier wallets. The deploying signer becomes buyer. The constructor ABI requires an address; Python callers must use `CalldataAddress(supplier_address)`, not raw bytes or an ordinary string. In Studio, use the address ABI input type.

1. Buyer: `lock_order`, passing the text of `examples/order.json` as one JSON string argument.
2. Read `get_documents`; copy `order.canonical_sha256`.
3. Supplier: `accept_order` with that hash.
4. Buyer: `lock_delivery` with the text of `examples/delivery.json`.
5. Supplier: `submit_invoice` with the text of `examples/invoice.json`.
6. Either participant: `evaluate`, allowing normal consensus.
7. Read `get_receipt`, `get_status` and events 1 through `event_count`. Independently verify hashes and network finality.

For a partial case, use a new deployment, delivered and billed quantity 10, invoice net 8500, tax 1700 and total 10200. For numeric discrepancy, deliver 10 but retain the 20-unit invoice. For semantic discrepancy, retain amounts and change delivered material to polyester. Real semantic outcomes require actual validator agreement; mocked fixtures cannot substitute for live proof.

No evidence correction, admin unlock or second invoice is supported. A partial result seals the instance. `sealed` is application state, not blockchain finality. Verify network status separately before relying on a receipt. There are no payment methods.
