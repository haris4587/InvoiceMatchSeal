# Intelligent Contracts submission

## Name

InvoiceMatchSeal

## Description

A standalone GenLayer Intelligent Contract that reconciles a supplier invoice against a mutually accepted purchase order and buyer-attested delivery. Deterministic accounting catches overbilling, price, tax and total errors; independent AI validators assess whether billed and delivered descriptions actually match the ordered goods or service scope. It produces immutable, hash-bound reconciliation receipts without payment authority.

## Why this matters

Correct quantities and prices do not prove the right goods arrived. A delivery may substitute polyester for cotton, change grade or omit required service scope while the invoice total remains unchanged. InvoiceMatchSeal separates accounting from semantic identity and records exactly which immutable evidence and classifications produced the result.

## GenLayer consensus

The contract uses real `gl.vm.run_nondet_unsafe` execution. The leader reviews committed descriptions; validators independently perform the same task without putting the leader's answer in their own prompt. Reports must contain exact quotes from all three corresponding descriptions. Validators compare the complete per-line semantic classification vector while allowing different explanations. The outcome, seal state, evidence references and decision hash are deterministic. This is substantive semantic consensus, not a single external model response stored on-chain or a JSON-only validator.

## State and safeguards

Buyer locks order/delivery; supplier accepts the exact canonical order hash and locks invoice. All evidence is write-once. Evaluation is participant-only, with three successful attempts at most for inconclusive reviews, exact raw/canonical commitments, append-only events and domain-bound receipts. No payments, token approvals, admin overrides, arbitrary URLs or retrieval tools exist. Wallet provenance and semantic consistency cannot prove real-world authenticity or physical delivery.

## Reviewer entry points

- Source: `contracts/invoice_match_seal.py`; SDK ABI: `docs/abi.json`.
- Inputs: `examples/order.json`, `delivery.json`, `invoice.json`.
- Checks: `pytest`, `genvm-lint check`, `genvm-lint typecheck`.
- Reproducible mocked demo: `python scripts/offline_demo.py`.
- Real hosted Studio proof: `docs/LIVE.md` and `docs/live-demo.json`.
- Independent receipt verifier: `scripts/verify_receipt.py`.
- Design and boundaries: `docs/ARCHITECTURE.md`, `docs/EVIDENCE.md`, `SECURITY.md`.

## Category and limitations

**Intelligent Contracts**: a standalone reusable primitive with developer tooling and no frontend. It is not an application submission or a milestone update to an accepted project. One invoice/obligation per instance; no global deduplication, amendments, fractional quantities, arbitrary commercial tax rules, PDF authentication or payment execution. Offline tests explicitly use mocked AI. Consult the live evidence for actual execution and finality. Approval and points are determined by the program; none are claimed.
