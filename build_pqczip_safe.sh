#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER="${PQC_WRAPPER:-}"
if [[ "${1:-}" == "--wrapper" && -n "${2:-}" ]]; then WRAPPER="$2"; shift 2; fi
if [[ -z "$WRAPPER" ]]; then
  for c in "$ROOT/pah_wrap_improved.py" "$ROOT/../PQC-Containers/pah_wrap_improved.py"; do
    [[ -f "$c" ]] && { WRAPPER="$c"; break; }
  done
fi
if [[ -z "$WRAPPER" ]] && command -v pah_wrap_improved.py >/dev/null 2>&1; then WRAPPER="$(command -v pah_wrap_improved.py)"; fi
if [[ -z "$WRAPPER" || ! -f "$WRAPPER" ]]; then
  printf 'PQC Scout-Knife wrapper not found.\n' >&2
  printf 'Get the public tooling from: https://github.com/DigiMancer3D/PQC-Containers\n' >&2
  printf 'Then run: PQC_WRAPPER=/path/to/PQC-Containers/pah_wrap_improved.py bash ./build_pqczip_safe.sh\n' >&2
  exit 2
fi
PYTHON="${PYTHON:-python3}"; command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
# COPY-ONLY staging. The public release and user data are never moved, consumed, shredded or rewritten.
for f in README.md PQCZIP_README.md CRYPTO_RELEASE_README.md RoloDesk_v0.3.4.html rolodesk_release.py rolodesk_local.py run_local.sh run_local.ps1 linux_desktop.sh manifest.webmanifest sw.js build_pqczip_safe.sh; do
  [[ -f "$ROOT/$f" ]] && cp -a "$ROOT/$f" "$TMP/"
done
for f in rolodesk-192.png rolodesk-512.png; do [[ -f "$ROOT/$f" ]] && cp -a "$ROOT/$f" "$TMP/"; done
"$PYTHON" "$WRAPPER" "$TMP" --container --name "RoloDesk_v0.3.4_PUBLIC" \
  --algorithm hybrid --output-dir "$ROOT" --keep-source --keep-archives --vanity-prefix RoloDesk_
printf 'Hybrid PQCZIP build requested with copy-safe --keep-source handling.\nOriginal RoloDesk release files were not moved or destroyed.\n'
