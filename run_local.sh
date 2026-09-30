#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  if command -v python3 >/dev/null 2>&1; then PYTHON=python3
  elif command -v python >/dev/null 2>&1; then PYTHON=python
  else printf 'Python 3 is required for local-server mode. The standalone HTML can still be opened directly.\n' >&2; exit 1
  fi
fi
exec "$PYTHON" "$ROOT/rolodesk_local.py" serve "$@"
