# State and consensus design

## State machine

One contract instance = one purchase order and one invoice. The deployer is buyer. The constructor fixes a distinct, nonzero supplier address; there is no role transfer. The domain includes policy version, chain ID, contract address, buyer and supplier.

1. Buyer locks order. Order fields and terms can never change.
2. Supplier accepts precisely the order's canonical SHA-256. This is explicit consent to prices, tolerances, specifications and tax conventions.
3. Buyer locks delivery and supplier locks invoice, in either order. Both require acceptance; each is write-once.
4. Either party evaluates after both documents exist. Accounting discrepancies finalize without calling AI.
5. Otherwise independent semantic consensus returns a grounded report. Determinate outcomes seal immediately. An inconclusive receipt can be reevaluated on unchanged documents, at most three successfully recorded attempts total. The third seals regardless of outcome.

Malformed model output, call failures and validator disagreement do not become approval or a synthetic “consensus succeeded” receipt. Transaction failure leaves deterministic state unchanged under GenVM rollback. Network rotations/retries are protocol behavior, separate from the three successful application attempts. Each attempt makes one model call per executing leader/validator path; there is no contract-side retry loop. No participant can amend evidence to shop for an outcome. New obligations need new deployments, and downstream systems must independently prevent duplicated real-world obligations.

## Deterministic checks

Schema validation rejects unknown keys, duplicate object keys, duplicate line IDs, booleans/floats used as integers, invalid bounds, unknown line references, unsupported currencies and missing receipt lines. Here “currency” validation means a three-uppercase-letter label plus exact equality, not an ISO database lookup. `minor_exponent` is the parties' chosen scale.

A delivery outside ordered quantity or unit is a discrepancy, even when unbilled. Every invoice quantity must be <= both ordered and received. Units match exactly. Prices may differ only by the locked absolute per-unit tolerance. Invoice net must equal quantity × invoice unit price. Tax uses the order's fixed basis-point rate, rounded half-up per line; invoice tax must equal it exactly. Invoice total is compared against the sum of recomputed line nets and taxes, with a separate locked absolute total tolerance. No floating point or external arithmetic oracle is used.

Partial means fewer billed units or omitted order lines. A partial result seals the single-invoice scope; it does not claim the entire purchase order was fulfilled.

## Meaningful nondeterministic work

A matching PO ID or price does not establish item identity: 500 gsm cotton and polyester towels may cost the same. The review compares each billed line's ordered specification with both delivery and invoice descriptions, including locked substitution/service-scope terms. It normalizes only meaning, not monetary values. Different materials, grade, model, unauthorized substitutions or unfinished required service scope are discrepancies; inadequate detail is unclear.

The leader prompt contains only immutable JSON evidence and fixed instructions. The validator does **not** feed the proposed answer into its own prompt: it executes the same independent task, validates its own report and compares the complete `(line ID, finding)` vector. Quote wording and explanations may vary. This is stronger than a JSON-only format check and is intentionally stricter than merely comparing the aggregate outcome.

Every `SAME`, `DIFFERENT` and `UNCLEAR` classification needs a nonempty exact substring from each relevant line description and a bounded explanation. Quotes establish source grounding, not semantic correctness; independent judgments remain essential. Embedded commands are explicitly untrusted, and there are no web/tools for the model to invoke. Prompt defenses are best effort; they cannot prove immunity to injection or correlated model mistakes.

`run_nondet_unsafe` is called positionally, with nested closures capturing only immutable local evidence and prompt data. No storage writes happen in nondeterministic blocks. Leader failures are never validator-approved. Deterministic code revalidates successful reports before building receipts.

## Events and receipts

Every successful write appends one `TreeMap[u32,str]` event. At most seven events exist: order, acceptance, delivery, invoice and three evaluations. The receipt for each evaluation lives forever inside its event even when `latest` changes. Hash preimages and external verification are documented in EVIDENCE.md. The external verifier checks hash/state/evidence consistency and needs a trusted on-chain head to prevent an attacker replacing the entire fabricated history. It does not rerun AI or attest network finality.
