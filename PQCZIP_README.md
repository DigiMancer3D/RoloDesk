# RoloDesk v0.3.4 — PQCZIP Guide

RoloDesk ships a PQCZIP-style `.pqcasset` beside the normal ZIP/HTML release.

## Public PQC tooling

DigiMancer3D PQC Containers / PQC Scout-Knife:

https://github.com/DigiMancer3D/PQC-Containers

The repository currently exposes `pah_wrap_improved.py` and the supporting PQC container tooling.

## Included RoloDesk PQCZIP

```text
PQCZIP_RoloDesk_v0.3.4_PUBLIC_STRUCTURAL.pqcasset
```

This file is a **PAH1 structural PQCZIP transport** with privacy-safe relative entry names and per-entry SHA-256 structural authentication placeholders.

It is deliberately described as **structural**, not as a claim that the package itself has received the complete hybrid Falcon/SPHINCS+/other post-quantum signing path from your local Scout-Knife stack.

## Build the full local hybrid form

Clone or obtain the public tooling:

```bash
git clone https://github.com/DigiMancer3D/PQC-Containers.git
```

Then from the RoloDesk release directory:

```bash
PQC_WRAPPER=/path/to/PQC-Containers/pah_wrap_improved.py \
  bash ./build_pqczip_safe.sh
```

or:

```bash
bash ./build_pqczip_safe.sh --wrapper /path/to/PQC-Containers/pah_wrap_improved.py
```

The wrapper also checks a sibling `../PQC-Containers/pah_wrap_improved.py` and an executable `pah_wrap_improved.py` available on `PATH`.

## RoloDesk's non-destructive rule

PQC Scout-Knife can implement digital-scarcity behaviors in which retrieval may consume or clean protected internal items. That is **not** the intended RoloDesk import/export behavior.

The RoloDesk bridge therefore:

1. creates a temporary staging directory,
2. **copies** the public release files into it,
3. invokes Scout-Knife with `--keep-source`,
4. retains the original RoloDesk files,
5. deletes only its temporary staging directory when complete.

The original RCC/RDC/user file must never be consumed simply because the user imports, exports, backs up, or shares it.

## What goes into the PQCZIP

Only the public runtime/docs are staged:

- RoloDesk HTML
- README files
- local launcher/server scripts
- PWA manifest/service worker/icons
- copy-safe PQCZIP bridge

Development logs, test reports, user data, absolute source-device paths, caches, and prior `.pqcasset` outputs are excluded from the staging list.

## Import/export-safe policy

For RoloDesk data containers, use the equivalent of:

```text
open / list / preview -> non-destructive
export / import       -> copy-safe
source file           -> preserved
```

Do not use a scarcity retrieval mode against a user's only copy of a RoloDesk database.

## Link transport

PQCZIP is a file transport. A full PQCZIP encoded directly into a browser URL usually becomes much larger due to URL/base64 overhead and can exceed browser/app limits.

RoloDesk therefore uses **RoloDesk Link v1** or **Itty.bitty v2** for small card/deck snapshots, while PQCZIP remains the better transport for full public application packages and larger protected datasets.

## Protect/sign an individual RoloDesk data export

RoloDesk v0.3.4 also includes `rolodesk_release.py` for a minimal copy-safe data-release workflow.

Create a SHA-256/external-signing manifest:

```bash
python3 ./rolodesk_release.py manifest MyExport.rdx
```

Copy-safely wrap that export through the full PQC Scout-Knife hybrid path:

```bash
python3 ./rolodesk_release.py pqc-wrap MyExport.rdx \
  --wrapper /path/to/PQC-Containers/pah_wrap_improved.py
```

Extract a received container from a **temporary copy** so the received original is not exposed to scarcity semantics:

```bash
python3 ./rolodesk_release.py pqc-extract Received.pqcasset \
  --wrapper /path/to/PQC-Containers/pah_wrap_improved.py \
  --output-dir ./received
```

See `CRYPTO_RELEASE_README.md` for browser-native P-256 signatures, recipient locks, Bitcoin/secp256k1 release manifests, and PQC handoff guidance.
