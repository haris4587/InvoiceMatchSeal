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
