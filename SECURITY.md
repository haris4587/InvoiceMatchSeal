# Security and limitations

## Authorization and immutability

The buyer is the deployer. A distinct, nonzero supplier is fixed at construction. Buyer alone locks order/delivery; supplier alone accepts order/submits invoice; only these parties evaluate. All records are immutable. No admin, upgrade, deletion, arbitrary write, payment, token approval, cross-contract call, URL request, secret or external signing key exists in the contract.

Supplier acceptance is a wallet transaction over the canonical order commitment. Delivery is buyer-attested and invoice supplier-attested. These roles can be mistaken, compromised or dishonest. Parties can collude. The contract authenticates submission provenance and consistency, not physical goods or document authenticity. It performs no signature forensics, issuer lookup, OCR or external identity verification.

## Resource bounds

Each submitted JSON/model string is at most 24,000 UTF-8 bytes. Maximum 12 lines/document, descriptions 8–512 characters, order terms 10–2,000, model reasons 15–600, identifiers 1–48 ASCII characters. Quantities are whole units <= 10^9, prices <= 10^9 minor units, tax 0–10,000 basis points, tolerances 0–100 minor units. There are at most three committed semantic attempts, seven history events and one model call per nondeterministic execution. Protocol validator count/rotations have separate network limits and costs. Rejecting oversized model output happens after the provider returns; provider-side generation cost is controlled by network/provider policy, not a claimed hard token cap in this contract.

Nested or malformed JSON fails closed. Exact schema validation rejects nonfinite/float numeric values, booleans as integers and duplicate keys. Model reports are revalidated before state writes. Unavailable/malformed leader or validator output cannot yield `MATCHED`. A model outage may make a transaction fail to reach consensus; it is not converted to a successful receipt.

## AI and commercial risks

Prompt strings and commercial descriptions are untrusted evidence. Fixed instructions demand independent review, prohibit following embedded commands/links, and require exact quotes. A validator repeats semantic reasoning without leader-answer contamination. These defenses do not guarantee correctness: correlated models may accept misleading descriptions, copied quotes may be semantically irrelevant, and adversarial documents may fool a quorum. Human commercial review remains necessary.

Numeric facts are explicitly structured wallet attestations. Narrative quantities/prices are not parsed by the model into arithmetic authority. A supplier can enter false but consistent structured invoice values; a buyer can falsely attest delivery. Terms must stay within the supported accounting conventions. Tax rates are mutually agreed inputs, not legal/tax guidance. No FX, discounts, fractional quantities, shipping fees, global deduplication, amendments or multi-invoice accounting is supported. A final discrepancy has no in-contract challenge/amendment path; resolve externally with both parties. Only inconclusive reviews can be retried, bounded by three total receipts.

## Public data and deployment

All order, delivery, invoice and model output text is public. Do not submit confidential customer or supplier data. Demo fixtures are synthetic. Demo wallet keys are local, ignored, generated only for test use and never included in evidence files. Do not send valuable funds to demo addresses or the contract. Script funding uses only hosted Studio test tokens.

Reconciliation `sealed` means the application refuses more attempts, not blockchain finality. Verify the GenLayer transaction is finalized and anchor the receipt verifier to the chain's actual domain/head. An offline hash chain alone cannot prove blockchain inclusion or prevent a wholly fabricated replacement history.

Report suspected issues privately to the repository owner through their available GitHub contact mechanism. No private security contact or audit certification is claimed. Do not put live invoice data or private keys in public issues.
