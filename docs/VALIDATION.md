# Validation report

Date: 2026-11-03.

## Automated verification

- **60 tests pass** with Python 3.12.14, `genlayer-test==0.29.2`, `pytest==9.2.0` and pinned GenVM v0.2.16 SDK.
- `genvm-lint check` passes AST lint and full SDK semantic validation.
- `genvm-lint typecheck` passes with no type errors.
- SDK schema extraction confirms five writes, four views and one constructor parameter; see `abi.json`.
- The mocked offline demo exports a receipt/event chain accepted by the separate verifier.

Coverage includes lifecycle/permissions, immutable locks, supplier hash acceptance, all outcomes, accounting discrepancy codes, rounding/tolerance boundaries, maximum 12-line input, UTF-8/raw/canonical hashes, unknown/missing/duplicate fields, invalid numeric types/bounds, prompt isolation, invented quotes, malformed model output, independent validator disagreement, different line classifications with the same aggregate outcome, equivalent prose, outages, bounded retries, append-only history and tampering detection.

Direct mode uses mocked AI. Tests explicitly execute the captured validator with separately swapped response fixtures. The injection test validates prompt separation and an adversarial fixture, not empirical model immunity. Unit tests do not prove distributed consensus, live model accuracy or production readiness. This is not a third-party security audit.

## Live verification

Hosted Studio uses real model calls and normal validator consensus. Both matching and semantic-substitution scenarios passed: `MATCHED` and `DISCREPANCY`, respectively. All 12 transactions are finalized with successful VM executions, agreeing validators, deployed-source equality and verified event chains. Exact evidence is in `live-demo.json` and `live-substitution.json`, summarized in `LIVE.md`. A sealed reconciliation receipt and an accepted transaction must not be confused with verified blockchain finality.

## Reproduce

```bash
python -m pip install -r requirements-dev.txt
pytest
genvm-lint check contracts/invoice_match_seal.py
genvm-lint typecheck contracts/invoice_match_seal.py
python scripts/offline_demo.py
python scripts/verify_receipt.py examples/offline-receipt.json
```

GitHub Actions repeats the checks and verifies the generated ABI matches source. [The source-build run passed](https://github.com/haris4587/InvoiceMatchSeal/actions/runs/41598207764). Machine-readable lint and test logs are committed alongside this report.
