#!/usr/bin/env python3
"""RoloDesk public release helper.

Public-safe rules:
- never stores absolute source paths in manifests;
- never moves, rewrites, shreds, or deletes the user's source export;
- PQC wrap stages a copy and requests Scout-Knife --keep-source;
- PQC extract operates on a temporary copy of the container.

This helper verifies SHA-256 integrity. External Bitcoin/PQC signature verification
is intentionally delegated to the wallet/tool that implements that signature scheme.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROFILE = "RoloDeskRelease1"
RELEASE = "0.3.4"
PQC_REPO = "https://github.com/DigiMancer3D/PQC-Containers"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def manifest_for(path: Path, profile: str = "external") -> dict:
    digest = sha256_file(path)
    created = utcnow()
    message = "\n".join([
        "RoloDesk Release v1",
        f"Name: {path.name}",
        f"SHA256: {digest}",
        f"Created: {created}",
    ])
    return {
        "format": PROFILE,
        "version": 1,
        "app": "RoloDesk",
        "release": RELEASE,
        "created": created,
        "file": {
            "name": path.name,
            "size": path.stat().st_size,
            "sha256": digest,
        },
        "signingMessage": message,
        "profile": profile,
        "externalSignature": {
            "scheme": "",
            "signerIdentifier": "",
            "signature": "",
        },
        "notes": (
            "SHA-256 verifies file-byte integrity. For Bitcoin/secp256k1, bitcoin-like, "
            "or PQC signatures, sign the exact signingMessage using the matching wallet/tool, "
            "then attach the resulting signature metadata."
        ),
    }


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve_wrapper(value: str | None) -> Path:
    candidates = []
    if value:
        candidates.append(Path(value).expanduser())
    env = __import__("os").environ.get("PQC_WRAPPER")
    if env:
        candidates.append(Path(env).expanduser())
    here = Path(__file__).resolve().parent
    candidates += [here / "pah_wrap_improved.py", here.parent / "PQC-Containers" / "pah_wrap_improved.py"]
    found = shutil.which("pah_wrap_improved.py")
    if found:
        candidates.append(Path(found))
    for p in candidates:
        if p.is_file():
            return p.resolve()
    raise SystemExit(
        "PQC Scout-Knife wrapper not found. Obtain it from:\n"
        f"  {PQC_REPO}\n"
        "Then pass --wrapper /path/to/PQC-Containers/pah_wrap_improved.py\n"
        "or set PQC_WRAPPER."
    )


def cmd_manifest(args) -> int:
    src = Path(args.file).expanduser().resolve()
    if not src.is_file():
        raise SystemExit(f"File not found: {src}")
    out = Path(args.output).expanduser() if args.output else src.with_name(src.stem + ".rdrelease.json")
    write_json(out, manifest_for(src, args.profile))
    print(out)
    return 0


def cmd_verify(args) -> int:
    src = Path(args.file).expanduser().resolve()
    man = json.loads(Path(args.manifest).expanduser().read_text(encoding="utf-8"))
    if man.get("format") != PROFILE:
        raise SystemExit("Not a RoloDesk release manifest")
    expected = str(man.get("file", {}).get("sha256", "")).lower()
    actual = sha256_file(src)
    ok = bool(expected) and expected == actual
    print(json.dumps({"sha256_match": ok, "expected": expected, "actual": actual}, indent=2))
    return 0 if ok else 1


def cmd_attach(args) -> int:
    src = Path(args.manifest).expanduser().resolve()
    man = json.loads(src.read_text(encoding="utf-8"))
    if man.get("format") != PROFILE:
        raise SystemExit("Not a RoloDesk release manifest")
    signature = Path(args.signature_file).expanduser().read_text(encoding="utf-8").strip() if args.signature_file else args.signature
    if not signature:
        raise SystemExit("Provide --signature or --signature-file")
    man["externalSignature"] = {
        "scheme": args.scheme,
        "signerIdentifier": args.signer,
        "signature": signature,
        "attachedAt": utcnow(),
        "verification": "Verify with the matching external wallet/tool; RoloDesk helper does not claim scheme-level verification.",
    }
    out = Path(args.output).expanduser() if args.output else src.with_name(src.stem + ".signed.json")
    write_json(out, man)
    print(out)
    return 0


def cmd_show_message(args) -> int:
    man = json.loads(Path(args.manifest).expanduser().read_text(encoding="utf-8"))
    print(man.get("signingMessage", ""))
    return 0


def cmd_pqc_wrap(args) -> int:
    src = Path(args.file).expanduser().resolve()
    if not src.is_file():
        raise SystemExit(f"File not found: {src}")
    wrapper = resolve_wrapper(args.wrapper)
    outdir = Path(args.output_dir).expanduser().resolve() if args.output_dir else src.parent
    outdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rolodesk-pqc-wrap-") as td:
        stage = Path(td) / "release"
        stage.mkdir()
        shutil.copy2(src, stage / src.name)
        sidecar = src.with_name(src.stem + ".rdrelease.json")
        if sidecar.is_file():
            shutil.copy2(sidecar, stage / sidecar.name)
        cmd = [
            sys.executable, str(wrapper), str(stage),
            "--container", "--name", f"RoloDesk_release_{src.stem}",
            "--algorithm", "hybrid", "--output-dir", str(outdir),
            "--keep-source", "--keep-archives", "--vanity-prefix", "RoloDesk_",
        ]
        print("Running copy-safe PQC wrap. Source file remains untouched.")
        return subprocess.run(cmd, check=False).returncode


def cmd_pqc_extract(args) -> int:
    src = Path(args.container).expanduser().resolve()
    if not src.is_file():
        raise SystemExit(f"Container not found: {src}")
    wrapper = resolve_wrapper(args.wrapper)
    outdir = Path(args.output_dir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rolodesk-pqc-extract-") as td:
        copied = Path(td) / src.name
        shutil.copy2(src, copied)
        cmd = [sys.executable, str(wrapper), str(copied), "--extract", "--output-dir", str(outdir)]
        print("Extracting from a temporary copy; the original PQC container remains untouched.")
        return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RoloDesk public-safe release/PQC helper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    q=sub.add_parser("manifest"); q.add_argument("file"); q.add_argument("--profile",choices=["sha256","external"],default="external"); q.add_argument("--output"); q.set_defaults(func=cmd_manifest)
    q=sub.add_parser("verify"); q.add_argument("file"); q.add_argument("manifest"); q.set_defaults(func=cmd_verify)
    q=sub.add_parser("show-message"); q.add_argument("manifest"); q.set_defaults(func=cmd_show_message)
    q=sub.add_parser("attach"); q.add_argument("manifest"); q.add_argument("--scheme",required=True); q.add_argument("--signer",required=True); g=q.add_mutually_exclusive_group(required=True); g.add_argument("--signature"); g.add_argument("--signature-file"); q.add_argument("--output"); q.set_defaults(func=cmd_attach)
    q=sub.add_parser("pqc-wrap"); q.add_argument("file"); q.add_argument("--wrapper"); q.add_argument("--output-dir"); q.set_defaults(func=cmd_pqc_wrap)
    q=sub.add_parser("pqc-extract"); q.add_argument("container"); q.add_argument("--wrapper"); q.add_argument("--output-dir",required=True); q.set_defaults(func=cmd_pqc_extract)
    args=parser.parse_args(); raise SystemExit(args.func(args))
