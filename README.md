# InvoiceMatchSeal

**A standalone GenLayer Intelligent Contract for evidence-backed purchase-order, delivery and invoice reconciliation.**

A hotel orders 20 white cotton bath towels at €8.50 each. A supplier invoices “bath linen” at the agreed total, but the buyer records polyester towels instead. Matching totals cannot establish that the ordered goods arrived. InvoiceMatchSeal combines deterministic accounting with independent AI-validator review of the actual item specifications.

One deployed instance binds one buyer wallet, one supplier wallet, one purchase order, one final delivery statement and one invoice. It returns `MATCHED`, `PARTIAL_MATCH`, `DISCREPANCY` or `INCONCLUSIVE`, with immutable document commitments and independently verifiable, hash-chained reconciliation receipts. **It never transfers funds or authorizes payment.**

## What makes this an Intelligent Contract

- The buyer locks structured order terms; the supplier explicitly accepts the canonical order hash.
- Only the buyer can attest delivery; only the supplier can submit the invoice. Both documents are immutable, and either participant can request reconciliation.
- Python checks whole-unit quantities, units, integer minor-unit prices, per-line taxes and invoice totals. Known accounting discrepancies need no AI call.
- When accounting passes, `gl.vm.run_nondet_unsafe` invokes real GenLayer nondeterministic execution. The leader reviews item identity, grade, substitution rules and service scope. Each validator independently repeats that task without seeing the leader's proposed answer in its prompt.
- Consensus requires the same **per-line semantic classification**, not identical prose. Every proposed and independent review must also satisfy an exact schema and contain verbatim evidence quotes from each corresponding line.
- An unavailable model or malformed review cannot create an approval. A successful `UNCLEAR` review produces `INCONCLUSIVE`, with at most three recorded attempts on the same evidence.

The AI classification is only one input. The final outcome, seal state, evidence references, accounting findings and decision hash are calculated deterministically. See [consensus and state design](docs/ARCHITECTURE.md).

## Outcomes

| Outcome | Exact meaning |
|---|---|
| `MATCHED` | All billed descriptions independently judged consistent with the order and delivery; no accounting discrepancies; the invoice covers every order line at the full ordered quantity. |
| `PARTIAL_MATCH` | Every billed line is supported and accounting is consistent, but the invoice omits an order line or bills fewer units than ordered. This is a final single-invoice receipt, not permission for another invoice on this instance. |
| `DISCREPANCY` | A deterministic discrepancy exists, or any semantic line is `DIFFERENT`. A proven discrepancy takes precedence over ambiguity elsewhere. |
| `INCONCLUSIVE` | Accounting passes, no line is `DIFFERENT`, and at least one line is `UNCLEAR`. Three such attempts seal the instance as inconclusive. |

`sealed` is application state; it does **not** mean the GenLayer transaction has reached network finality. Check the network transaction separately.

## Live verification

Deployed and verified on hosted GenLayer Studio: [`0xB6f407d63B9730e45FED492E4c1acd17F0EC814D`](https://explorer-studio.genlayer.com/contracts/0xB6f407d63B9730e45FED492E4c1acd17F0EC814D). The full six-transaction lifecycle is finalized with a real-AI `MATCHED` result and agreeing validators. [Proof and reproduction](docs/LIVE.md).

## Run and verify

Python 3.12+ is required. The first SDK download can take a few minutes.

```bash
python -m pip install -r requirements-dev.txt
pytest
python scripts/offline_demo.py
genvm-lint check contracts/invoice_match_seal.py
genvm-lint typecheck contracts/invoice_match_seal.py
genvm-lint schema contracts/invoice_match_seal.py --output /tmp/invoice-abi.json
python scripts/verify_receipt.py examples/offline-receipt.json
```

The offline demo and unit tests use **mocked AI through the official GenLayer direct-mode harness**. They are not evidence of live model quality or distributed consensus. See [validation](docs/VALIDATION.md) and [deployment](docs/DEPLOYMENT.md) for the hosted Studio lifecycle and its exact verification status.

## Contract API

Every document argument is a JSON **string**, not a JSON object. All views return JSON strings, except `get_receipt()` returns an empty string before evaluation.

| Method | Caller | Purpose |
|---|---|---|
| `constructor(supplier: Address)` | Buyer | Fix distinct nonzero buyer/supplier roles and chain/contract domain. |
| `lock_order(order_json: str)` | Buyer | Validate and lock the sole purchase order. |
| `accept_order(canonical_sha256: str)` | Supplier | Accept the exact canonical order hash from `get_documents()`. |
| `lock_delivery(delivery_json: str)` | Buyer | Lock the final receipt after order acceptance; every order line must appear, including zero quantities. |
| `submit_invoice(invoice_json: str)` | Supplier | Lock the sole invoice after acceptance. It may arrive before or after delivery. |
| `evaluate()` | Either participant | Run accounting and, when needed, independent semantic consensus. |
| `get_status()` | Anyone | Read immutable identities, lifecycle flags, attempt count and event head. |
| `get_documents()` | Anyone | Read canonical document data and original byte/canonical commitments. |
| `get_receipt()` | Anyone | Read the latest reconciliation receipt and decision hash. |
| `get_event(sequence: int)` | Anyone | Read any append-only event; numbering starts at 1. |

Realistic synthetic input documents are in [examples](examples). [EVIDENCE.md](docs/EVIDENCE.md) specifies every accepted field, bound, accounting convention and hash preimage.

## Trust boundaries and scope

Wallets authenticate **who submitted a statement**, not its real-world truth. Semantic agreement cannot authenticate signatures, physical delivery, identity documents or bank records. Participants can lie or collude. Hashes prove byte/content binding, not truth. Independent AI review reduces reliance on one model but can still make mistakes or fail to reach consensus.

This version handles one invoice against a single agreed obligation. It does not support amended evidence, multiple invoices, fractional quantities, discounts, shipping charges, FX, tax-law validation or payments. Model spec ambiguities should yield `INCONCLUSIVE`; complex commercial terms should be split into explicit supported line items before locking. Duplicate billing **across separate deployments is outside its scope**. There is no global invoice registry, administrator override, upgrade hook or arbitrary web retrieval.

All submitted content and model prompts are public. Use synthetic or appropriately public descriptions, never confidential invoices. See [SECURITY.md](SECURITY.md).

## Submission and references

Prepared for **Intelligent Contracts**, not Projects: the deliverable is a reusable standalone contract primitive with no frontend. Submission copy and reviewer instructions are in [SUBMISSION.md](docs/SUBMISSION.md).

The implementation follows current official [GenLayer nondeterminism](https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism), [LLM calls](https://docs.genlayer.com/developers/intelligent-contracts/features/calling-llms), [testing](https://docs.genlayer.com/api-references/genlayer-test/direct), and [linter](https://docs.genlayer.com/api-references/genlayer-linter) documentation. Runtime dependency is pinned in the contract's first line. Architecture was informed by the commit/evidence/consensus patterns of [ProtocolLens](https://github.com/haris4587/ProtocolLens); the invoice-specific state machine, accounting rules, evidence protocol and tests are original to this repository.

MIT license. This is documentary reconciliation software, not an audit certification or payment instruction.
