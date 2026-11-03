# Live hosted Studio verification

Verified on 2026-11-03 with real AI calls and normal validator consensus. All six lifecycle transactions are FINALIZED and have successful VM execution; the deployed source bytes match the repository contract exactly.

- Network: hosted Studio, chain `61999`.
- Contract: [`0xB6f407d63B9730e45FED492E4c1acd17F0EC814D`](https://explorer-studio.genlayer.com/contracts/0xB6f407d63B9730e45FED492E4c1acd17F0EC814D).
- Source SHA-256: `e4bb8da252624f82ddee33edfb532e8e00b2ded20dd801383fb0115fef9900ce`.
- Outcome: **MATCHED** for the synthetic 20-unit cotton towel delivery/invoice.
- Finalized event head: `ee9724750fb0b61a336778367e54d40e2417f48390c50a6318e0b2d5c4a6c678`.
- Proof snapshot: [live-demo.json](live-demo.json).

| Method | Transaction | Status |
|---|---|---|
| deploy | [0xd81c137738…](https://explorer-studio.genlayer.com/tx/0xd81c1377382d411c8c8a42e8ace775942aad58547b69db0865b2e16da587a39f) | FINALIZED / VM SUCCESS |
| lock_order | [0xe7599560f6…](https://explorer-studio.genlayer.com/tx/0xe7599560f6d5a83b5ab706d679b805e01dd471c02464a75e9b2e414ab1ad2318) | FINALIZED / VM SUCCESS |
| accept_order | [0x36269a7c86…](https://explorer-studio.genlayer.com/tx/0x36269a7c86b6d0c3282f80f4d0e3ce8bbdebc86265a6e053c0d5fe349d703d0b) | FINALIZED / VM SUCCESS |
| lock_delivery | [0x5b5a85a668…](https://explorer-studio.genlayer.com/tx/0x5b5a85a6685ae657470cfb8cb48a0dadbe888a46135d812a9046cc96b77c94ba) | FINALIZED / VM SUCCESS |
| submit_invoice | [0xf1ae639fc9…](https://explorer-studio.genlayer.com/tx/0xf1ae639fc97ec1453018ed5ef26a091010fb378b689ee28b6100f148e6362a17) | FINALIZED / VM SUCCESS |
| evaluate | [0xafe43f6542…](https://explorer-studio.genlayer.com/tx/0xafe43f65421284d33a32d7b5365009ab811e7b692cdb795fbfc80afa1f666576) | FINALIZED / VM SUCCESS |

Independent read-only verification:

```bash
python scripts/verify_live.py
python scripts/verify_receipt.py docs/live-demo.json --expected-head ee9724750fb0b61a336778367e54d40e2417f48390c50a6318e0b2d5c4a6c678
```

The verifier separately fetches deployment input bytes, transaction finality and successful executions, agreeing validator votes, finalized getter state and the event chain. The proof snapshots are compact extracts; transaction hashes let reviewers retrieve current network data themselves. Agreement means the network accepted the outcome; votes need not be unanimous. The raw vote map preserves disagreements.

Studio is a hosted sandbox, not Bradbury or production. It may reset. This public synthetic test demonstrates execution and independent semantic consensus; it does not prove accuracy for arbitrary commercial documents or immunity to adversarial prompts. No actual payment was authorized or transferred.


## Same amounts, wrong material

A second instance kept all quantities, prices, taxes and invoice totals identical, but delivery explicitly reported polyester instead of the ordered cotton. Real semantic consensus returned **DISCREPANCY**, with a grounded `DIFFERENT` finding; arithmetic had no discrepancies. All six transactions are finalized, all returned VM executions succeeded, and deployed source bytes match the same contract.

- Contract: [`0xed891334A5066375Aa2d3ee3bBA9D5F98F8F9D40`](https://explorer-studio.genlayer.com/contracts/0xed891334A5066375Aa2d3ee3bBA9D5F98F8F9D40).
- Full compact proof: [live-substitution.json](live-substitution.json).
- Finalized head: `ca63bdfa8c813a1b0f4fb4653469b7a01575f8c27b8886d20b6d45775d8f6177`.

| Method | Transaction | Status |
|---|---|---|
| deploy | [0x23b10c6d00…](https://explorer-studio.genlayer.com/tx/0x23b10c6d006aa26db3a76cd9470a1aa595cf3d0ad6620b931ba93947e1c84178) | FINALIZED / VM SUCCESS |
| lock_order | [0xd06e6a0810…](https://explorer-studio.genlayer.com/tx/0xd06e6a0810aaa38b2fab5fec55c106e8342f885d0e304d8e7b98eea49626f3bf) | FINALIZED / VM SUCCESS |
| accept_order | [0xccc84c5bab…](https://explorer-studio.genlayer.com/tx/0xccc84c5bab5c76c44674185e655022f5325ef293a7f2425d24a38d45b96cf2e6) | FINALIZED / VM SUCCESS |
| lock_delivery | [0xf88e211838…](https://explorer-studio.genlayer.com/tx/0xf88e211838a83552e6a38027887c81218effc18f5bbd1048c8d24737ff73550c) | FINALIZED / VM SUCCESS |
| submit_invoice | [0x4ed3f9805a…](https://explorer-studio.genlayer.com/tx/0x4ed3f9805a1bf36dcde0d65c6c3d7d7fbe3db501e2dea13d4faeb58f0c9f86df) | FINALIZED / VM SUCCESS |
| evaluate | [0x01d48b5a97…](https://explorer-studio.genlayer.com/tx/0x01d48b5a9765310c2eda2d5ec00b610f755262a3f91efa6e3d73ab251fcb8810) | FINALIZED / VM SUCCESS |

Reproduce this scenario with `python scripts/live_demo.py --case substitution`. Independently recheck using `python scripts/verify_live.py docs/live-substitution.json`. The same two demo wallets participated; the contract instance and evidence history are separate.
