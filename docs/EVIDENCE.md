# Evidence protocol v1

This contract commits inline JSON evidence directly into GenLayer state. It never fetches URLs: network outages, redirects, mutable web pages and SSRF are absent from the evidence path. It needs no GitHub commit URL because the actual evidence bytes are supplied in the transaction. Existing PDF invoices must first be converted to explicitly agreed structured statements outside the contract; v1 does not authenticate or parse the original PDF.

## Accepted documents

See `examples/order.json`, `delivery.json` and `invoice.json` for complete valid inputs. All fields are required; extra fields are rejected.

| Document | Top-level fields | Line fields |
|---|---|---|
| Order | `order_id`, `currency`, `minor_exponent`, `price_tolerance_minor`, `total_tolerance_minor`, `terms`, `lines` | `id`, `description`, `unit`, `quantity`, `unit_price_minor`, `tax_bps` |
| Delivery | `order_id`, `receipt_id`, `lines` | `id`, `description`, `unit`, `quantity` |
| Invoice | `order_id`, `invoice_id`, `currency`, `total_minor`, `lines` | `id`, `description`, `unit`, `quantity`, `unit_price_minor`, `net_minor`, `tax_minor` |

IDs and unit labels match `[A-Za-z0-9_-]{1,48}`. Use unique stable PO line IDs in all documents. Order/invoice quantities are positive; delivery quantities may be zero. Delivery covers every PO line. Invoice may cover a subset, but cannot contain unknown lines. Quantities are integers in the stated unit; model/grade/specification belongs in `description`. Use separate explicitly quantified service milestones for whole-unit service invoices. `minor_exponent=2` means 850 minor units represents 8.50 currency units. Currency labels are not converted or looked up.

For invoice line net N = quantity × invoice unit_price_minor:

```
expected_tax_minor = (N * order_tax_bps + 5000) // 10000
expected_total_minor = sum(N + expected_tax_minor for all billed lines)
```

Tax rounds half-up independently per line. Tax and net must match exactly; only unit price and overall total have the separately agreed absolute minor-unit tolerances. No hidden fees, credits or discounts. A billed unit price within tolerance becomes the basis for that line's net/tax.

## Commitments and canonicalization

`raw_sha256` hashes the original input JSON string's UTF-8 bytes exactly, including whitespace. `raw_bytes` is that byte count. Raw text is available from the submitting transaction; the state stores the parsed canonical data and raw commitment, not another full raw copy.

`canonical_sha256` hashes UTF-8 of Python:

```python
json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(',', ':'))
```

Before canonicalization, lines are sorted lexicographically by ID. No Unicode normalization or whitespace trimming changes the submitted string values. Float/boolean numeric fields, duplicate object keys and unknown fields are rejected. Tests bind the raw and canonical commitments separately. Original raw commitment cannot be verified from canonical data alone; obtain exact transaction input bytes for that check.

The supplier accepts the order's canonical hash. Receipts bind canonical document hashes, the domain and the history predecessor. Both raw and canonical commitments live in the immutable document-lock events.

## Decision and event hashes

- `decision_hash`: SHA-256 of canonical UTF-8 receipt **before adding** `decision_hash`.
- `event_hash`: SHA-256 of canonical UTF-8 event **before adding** `event_hash`.
- Event preimage: `domain`, `sequence`, `previous_hash`, `actor`, `kind`, `payload`.
- Domain: `policy`, `chain_id`, `contract`, `buyer`, `supplier`.
- Genesis predecessor: 64 ASCII zeros. Sequence numbers start at 1.
- A reconciliation receipt contains `previous_event_hash`, pointing to the event immediately before its own `RECONCILED` event.

Use `get_event(1..event_count)` plus `get_receipt()` and `get_status()` to export a bundle. `scripts/verify_receipt.py` checks its chain, hashes, domains, roles, evidence references, receipt sequencing and seal flags. Supply `--expected-head` using a separately trusted finalized on-chain read to anchor the result. Verification is consistency/inclusion anchoring, not independent semantic re-adjudication.

## Example classifications

| Evidence | Expected result |
|---|---|
| 20 ordered, received and correctly billed cotton towels, same grade and size | MATCHED |
| 20 ordered, 10 received and correctly billed, identity established | PARTIAL_MATCH |
| 20 billed, 10 received | DISCREPANCY, no model call |
| Correct amounts, delivery explicitly says polyester in place of required cotton | DISCREPANCY after semantic consensus |
| Correct amounts, delivery says only “assorted linen” without material/grade | INCONCLUSIVE if validators agree detail is insufficient |
| Invalid JSON, invented quotes or unavailable model | Rejected write/consensus failure; no approval receipt |
