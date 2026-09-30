# RoloDesk v0.3.4 — Export Security & Cryptographic Release

RoloDesk separates **source-file security** from **export security**.

A protected RoloDesk is not a prison for your own data. After you unlock it, you may intentionally export a card, deck, or whole database in an open form or protect that specific export with a different mechanism.

## Export choices

### Open / unprotected export

Creates the requested standard/native file without export encryption. This works even when the source RoloDesk was password-protected.

Use this when you intentionally need a public/readable copy, for example a VCF contact card for another person.

If the selection contains password cards, RoloDesk gives an explicit warning before creating the unprotected copy.

### Password-protected RDX

`.rdx` means **RoloDesk Exchange**.

The selected export is wrapped with:

- PBKDF2-SHA-256
- 310,000 iterations
- random salt
- AES-256-GCM
- fresh random IV
- SHA-256 content digest

The export password is chosen at export time and is independent of the source database password.

### Recipient public-key RDX

For person-to-person transfer, RoloDesk can generate a recipient identity:

- RSA-OAEP 3072-bit / SHA-256 public/private key pair
- random AES-256-GCM content key per RDX
- content key wrapped to the recipient public key

The recipient shares only their `.rdpub`. They keep the encrypted `.rdkey` private.

This is **recipient encryption**, not a signature.

### Browser-native signed RDX

RoloDesk can generate a signing identity using:

- ECDSA P-256
- SHA-256

The private `.rdkey` signs the RDX. The public key and fingerprint are embedded in the RDX so RoloDesk can verify the package before import.

A valid signature proves the RDX matches the signing key. Trust in the human/organization behind that key still depends on how you verified the key fingerprint.

## SHA-256 release receipts

`SHA-256 receipt` produces a `.rdrelease.json` sidecar for the exact exported file.

SHA-256 provides **integrity**, not signer identity. It tells you whether the bytes still match the receipt.

## Bitcoin / bitcoin-like signatures

Bitcoin uses secp256k1 and wallet-specific message/signature conventions. Browser WebCrypto does not provide secp256k1 as a standard ECDSA curve, so RoloDesk does not fake compatibility by converting it to P-256.

Choose **External BTC / PQC signing manifest**. RoloDesk exports a `.rdrelease.json` containing the exact signing message and SHA-256 digest. Sign that message with your compatible Bitcoin/bitcoin-like wallet or signing tool.

An xpub is an extended **public** key. It can derive non-hardened public child keys, but it does not contain the private key required to sign. Therefore RoloDesk does not describe xpub as a "private-key unlock" mechanism.

To attach external signature metadata:

```bash
python3 ./rolodesk_release.py attach MyExport.rdrelease.json \
  --scheme bitcoin-message/secp256k1 \
  --signer "YOUR_PUBLIC_ADDRESS_OR_ID" \
  --signature-file signature.txt
```

RoloDesk can verify the file SHA-256. Verify the Bitcoin signature itself with the wallet/tool that implements the signature convention.

## PQC / Crypto.Chess / PQC Scout-Knife release

Public tooling:

https://github.com/DigiMancer3D/PQC-Containers

Create the browser export first (`.rdx`, `.rcc`, `.rdc`, etc.), then copy-safely wrap it through your PQC toolchain:

```bash
python3 ./rolodesk_release.py pqc-wrap MyExport.rdx \
  --wrapper /path/to/PQC-Containers/pah_wrap_improved.py
```

The helper stages a **copy**, invokes the hybrid wrapper with `--keep-source`, and never moves/shreds the original RoloDesk export.

To extract a received PQC container without risking scarcity behavior against the only original:

```bash
python3 ./rolodesk_release.py pqc-extract Received.pqcasset \
  --wrapper /path/to/PQC-Containers/pah_wrap_improved.py \
  --output-dir ./received_export
```

RoloDesk first copies the PQC container to a temporary location and extracts that copy. The original container remains untouched.

## Lawyer / records handoff example

1. Select the needed card/deck/database.
2. Choose a readable format or RCC/RDC.
3. Choose **Recipient public-key RDX** if the lawyer supplies a RoloDesk recipient `.rdpub`, or choose a normal password-protected RDX and exchange the password separately.
4. Optionally add **ECDSA P-256 signed RDX** for browser-native release identity.
5. For Bitcoin/PQC evidence, generate the external release manifest and sign its exact message with the matching external tool.
6. For the strongest RoloDesk/PQC workflow, wrap the resulting export with `rolodesk_release.py pqc-wrap`.

## Key safety

- `.rdpub` is intended to be shared.
- `.rdkey` contains a private key and is encrypted by the password you choose when generating it.
- Never send the recipient private key to the sender.
- Never treat an embedded public key as trusted merely because a signature verifies; compare the displayed fingerprint through a separate trusted channel when identity matters.
