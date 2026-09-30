#!/usr/bin/env python3
"""RoloDesk v0.3.4 loopback launcher.

Desktop app mode uses a dedicated Chromium-family app process so KDE Plasma can
associate the running window with rolodesk.desktop.  On a Wayland session the
RoloDesk Chromium wrapper deliberately uses XWayland: WM_CLASS=rolodesk is then
stable and matches StartupWMClass=rolodesk.  The rest of the desktop remains
native Wayland.
"""
from __future__ import annotations

import argparse
import http.server
import json
import mimetypes
import os
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from pathlib import Path

VERSION = "0.3.4"
APP = "RoloDesk_v0.3.4.html"
LINUX_APP_ID = "rolodesk"
LINUX_DESKTOP_FILE = "rolodesk.desktop"
ROOT = Path(__file__).resolve().parent
REGISTRY = Path(tempfile.gettempdir()) / "rolodesk-v034-servers.json"
mimetypes.add_type("application/manifest+json", ".webmanifest")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Permissions-Policy",
            "geolocation=(), camera=(), microphone=(), web-share=(self)",
        )
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self' data: blob:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "connect-src 'self'; frame-src 'none'; object-src 'none'; "
            "base-uri 'none'; form-action 'self'",
        )
        super().end_headers()

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/favicon.ico":
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        super().do_GET()

    def copyfile(self, source, outputfile):
        try:
            return super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError):
            return None

    def log_error(self, fmt, *args):
        msg = fmt % args
        if "Broken pipe" in msg or "Connection reset" in msg:
            return
        super().log_error(fmt, *args)


class Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        exc = sys.exception() if hasattr(sys, "exception") else None
        if isinstance(exc, (BrokenPipeError, ConnectionResetError)):
            return
        super().handle_error(request, client_address)


def _load_registry():
    try:
        obj = json.loads(REGISTRY.read_text())
        return obj if isinstance(obj, list) else []
    except Exception:
        return []


def _save_registry(rows):
    try:
        REGISTRY.write_text(json.dumps(rows, indent=2))
    except Exception:
        pass


def _alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False


def _prune():
    rows = [r for r in _load_registry() if _alive(r.get("pid", -1))]
    _save_registry(rows)
    return rows


def _register(pid, port):
    rows = [r for r in _prune() if int(r.get("pid", -1)) != pid]
    rows.append(
        {
            "pid": pid,
            "port": port,
            "root": str(ROOT),
            "version": VERSION,
            "started": time.time(),
        }
    )
    _save_registry(rows)


def _unregister(pid):
    _save_registry([r for r in _prune() if int(r.get("pid", -1)) != pid])


def find_port(start=8080, stop=8100):
    for port in range(start, stop + 1):
        with socket.socket() as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _chromium_profile() -> Path:
    data_home = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    # A name different from the first hotfix avoids stale locks/settings from it.
    profile = data_home / "rolodesk" / "chromium-app-profile-v2"
    profile.mkdir(parents=True, exist_ok=True)
    return profile


def choose_browser(url, app_mode=False, choice="auto"):
    if choice == "none":
        return None

    if os.name == "posix" and sys.platform != "darwin":
        import shutil

        requested = [] if choice == "auto" else [choice]
        normal = requested or [
            "librewolf",
            "firefox",
            "ungoogled-chromium",
            "chromium",
            "google-chrome",
        ]
        app = requested or [
            "ungoogled-chromium",
            "chromium",
            "google-chrome",
            "librewolf",
            "firefox",
        ]

        for name in (app if app_mode else normal):
            exe = shutil.which(name)
            if not exe:
                continue

            args = [exe]
            env = None

            if app_mode and ("chromium" in name or "chrome" in name):
                profile = _chromium_profile()
                args += [
                    "--app=" + url,
                    "--class=" + LINUX_APP_ID,
                    "--user-data-dir=" + str(profile),
                    "--no-first-run",
                    "--no-default-browser-check",
                ]

                # KDE Plasma on Wayland keys taskbar grouping/icon lookup from the
                # Wayland app_id.  Generic --app URL windows can be absorbed by an
                # existing browser process and keep the browser's identity.  A
                # dedicated process plus XWayland gives this wrapper a predictable
                # WM_CLASS of exactly "rolodesk", which matches rolodesk.desktop.
                if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
                    args.append("--ozone-platform=x11")

                env = os.environ.copy()
                env["CHROME_DESKTOP"] = LINUX_DESKTOP_FILE

            else:
                args.append(url)

            try:
                return subprocess.Popen(
                    args,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=env,
                    start_new_session=True,
                )
            except OSError:
                continue

    try:
        webbrowser.open(url, new=1)
    except Exception:
        pass
    return None


def serve(args):
    if not (ROOT / APP).is_file():
        raise SystemExit(f"Missing {APP}")

    if args.replace:
        stop_all()

    port = args.port or find_port()
    srv = Server(("127.0.0.1", port), QuietHandler)
    url = f"http://127.0.0.1:{port}/{APP}"
    _register(os.getpid(), port)

    closing = False

    def cleanup(*_):
        nonlocal closing
        if closing:
            return
        closing = True
        _unregister(os.getpid())
        threading.Thread(target=srv.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    print(f"RoloDesk v{VERSION} — local-only server\n{url}", flush=True)
    if port != 8080:
        print(
            f"Port 8080 is occupied; using {port}. Existing services were not touched.",
            flush=True,
        )

    browser = choose_browser(url, args.app_mode, args.browser)
    if args.browser != "none":
        print("Browser launch requested.", flush=True)

    # Do NOT tie server lifetime to the short-lived Chromium launcher process.
    # Chromium may daemonize or hand off startup; stopping here made earlier
    # desktop builds appear not to launch.  The next desktop launch uses
    # --replace, and rolodesk_local.py stop can end it explicitly.
    _ = browser

    try:
        srv.serve_forever(poll_interval=0.25)
    finally:
        _unregister(os.getpid())
        srv.server_close()


def status():
    rows = _prune()
    print("RoloDesk local-server status")
    if not rows:
        print("  No registered RoloDesk servers are running.")
        return
    for row in rows:
        print(
            f"  PID {row['pid']}  port {row['port']}  "
            f"v{row.get('version', '?')}  root={row.get('root', '')}"
        )


def stop_rows(rows):
    for row in rows:
        pid = int(row.get("pid", -1))
        if pid == os.getpid() or not _alive(pid):
            continue
        print(f"Stopping RoloDesk PID {pid}")
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            continue
        for _ in range(30):
            if not _alive(pid):
                break
            time.sleep(0.1)
    _prune()


def stop_current():
    here = str(ROOT)
    stop_rows([r for r in _prune() if r.get("root") == here])


def stop_all():
    stop_rows(_prune())


def main():
    parser = argparse.ArgumentParser(description="RoloDesk v0.3.4 local launcher")
    sub = parser.add_subparsers(dest="cmd")

    serve_parser = sub.add_parser("serve")
    serve_parser.add_argument("--port", type=int, default=0)
    serve_parser.add_argument("--replace", action="store_true")
    serve_parser.add_argument("--app-mode", action="store_true")
    serve_parser.add_argument(
        "--browser", default="auto", help="auto, none, or browser command name"
    )

    sub.add_parser("status")
    stop_parser = sub.add_parser("stop")
    stop_parser.add_argument("--all", action="store_true")

    args = parser.parse_args()

    if args.cmd in (None, "serve"):
        if args.cmd is None:
            args = argparse.Namespace(
                port=0, replace=False, app_mode=False, browser="auto"
            )
        return serve(args)
    if args.cmd == "status":
        return status()
    if args.cmd == "stop":
        return stop_all() if args.all else stop_current()


if __name__ == "__main__":
    main()
