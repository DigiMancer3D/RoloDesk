#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
APPDIR="$DATA_HOME/applications"
BINDIR="$HOME/.local/bin"
ICONROOT="$DATA_HOME/icons/hicolor"
DESKTOP="$APPDIR/rolodesk.desktop"
WRAP="$BINDIR/rolodesk"
APP_ID="rolodesk"

refresh_desktop() {
  command -v update-desktop-database >/dev/null 2>&1 \
    && update-desktop-database "$APPDIR" >/dev/null 2>&1 || true
  command -v gtk-update-icon-cache >/dev/null 2>&1 \
    && gtk-update-icon-cache -f -t "$ICONROOT" >/dev/null 2>&1 || true
  command -v kbuildsycoca6 >/dev/null 2>&1 \
    && kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
}

install_icons() {
  mkdir -p "$ICONROOT/192x192/apps" "$ICONROOT/512x512/apps"
  [[ -f "$ROOT/rolodesk-192.png" ]] && cp -f "$ROOT/rolodesk-192.png" "$ICONROOT/192x192/apps/rolodesk.png"
  [[ -f "$ROOT/rolodesk-512.png" ]] && cp -f "$ROOT/rolodesk-512.png" "$ICONROOT/512x512/apps/rolodesk.png"
}

case "${1:-install}" in
  install)
    [[ -f "$ROOT/rolodesk_local.py" ]] || {
      printf 'ERROR: Missing %s/rolodesk_local.py\n' "$ROOT" >&2
      exit 2
    }
    [[ -f "$ROOT/RoloDesk_v0.3.4.html" ]] || {
      printf 'ERROR: Missing %s/RoloDesk_v0.3.4.html\n' "$ROOT" >&2
      exit 2
    }

    mkdir -p "$APPDIR" "$BINDIR"
    install_icons

    cat >"$WRAP" <<EOF2
#!/usr/bin/env bash
set -Eeuo pipefail
exec python3 "${ROOT}/rolodesk_local.py" serve --app-mode --replace
EOF2
    chmod +x "$WRAP"

    cat >"$DESKTOP" <<EOF2
[Desktop Entry]
Version=1.0
Type=Application
Name=RoloDesk
GenericName=Local-first Rolodex
Comment=Local-first contacts, calendar, notes and password cards
Exec=${WRAP}
Icon=rolodesk
Terminal=false
Categories=Office;
StartupNotify=true
StartupWMClass=${APP_ID}
X-KDE-StartupNotify=true
EOF2
    chmod +x "$DESKTOP"

    if command -v desktop-file-validate >/dev/null 2>&1; then
      desktop-file-validate "$DESKTOP" || true
    fi
    refresh_desktop

    printf 'Installed RoloDesk desktop launcher.\n'
    printf 'Desktop entry: %s\n' "$DESKTOP"
    printf 'Icon:          rolodesk\n'
    printf 'Window class:  %s\n' "$APP_ID"
    printf 'Release dir:   %s\n' "$ROOT"
    ;;

  remove|uninstall)
    rm -f "$DESKTOP" "$WRAP"
    rm -f "$ICONROOT/192x192/apps/rolodesk.png" "$ICONROOT/512x512/apps/rolodesk.png"
    refresh_desktop
    printf 'Removed the RoloDesk desktop launcher and installed icon copies.\n'
    printf 'RoloDesk data files and browser app profile were not touched.\n'
    ;;

  *)
    printf 'Usage: bash ./linux_desktop.sh [install|remove|uninstall]\n' >&2
    exit 2
    ;;
esac
