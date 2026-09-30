# RoloDesk v0.3.4

> A local-first, four-deck Rolodex workspace for **Contacts, Calendar, Notes, and Password cards** — built as a self-contained browser application with optional PWA, desktop-launcher, encrypted native files, portable link snapshots, and PQCZIP transport.

**Public release:** `0.3.4`  
**Project home / intended repository:** https://github.com/DigiMancer3D/RoloDesk  
**PQCZIP tooling:** https://github.com/DigiMancer3D/PQC-Containers

RoloDesk was designed first around **CachyOS/Linux and Android**, while keeping the core application plain HTML/CSS/JavaScript so it remains useful on Windows, macOS, iOS/iPadOS, and other modern browsers.

---

## What RoloDesk is

RoloDesk presents four card decks as two paired Rolodexes:

| Rolodex A | Rolodex B |
|---|---|
| ☎ Contacts | 🔒 Passwords |
| ▦ Calendar | ▤ Notes |

The interface is intentionally spatial: cards peel away from the active card, the dial navigates dates or contact/password indexes, special actions roll down in the wooden menu, and the floating `＋` button acts as both **New Card** and the action-drawer control.

`＋` behavior:

- single click/tap → create a new card
- double click/tap → toggle the action drawer
- press-and-hold (~650 ms) → toggle the action drawer on mouse, touch, or pen

The page itself does not vertically scroll during normal deck use. Notes and roll-down menus can scroll internally when needed.

---

## Fastest way to use it

### Any desktop browser

Open:

```text
RoloDesk_v0.3.4.html
```

That is the widest-compatibility mode. File loading/saving works with normal browser pickers/downloads.

### Local-first server mode

The included local server binds only to `127.0.0.1`, picks another local port if 8080 is occupied, and serves the PWA files with restrictive browser security headers.

Linux/macOS:

```bash
bash ./run_local.sh
```

Windows PowerShell:

```powershell
.\run_local.ps1
```

Direct Python on any supported desktop:

```bash
python3 ./rolodesk_local.py serve
```

Useful process controls:

```bash
python3 ./rolodesk_local.py status
python3 ./rolodesk_local.py stop
python3 ./rolodesk_local.py stop --all
python3 ./rolodesk_local.py serve --replace
```

`stop --all` only stops servers that registered themselves as RoloDesk servers. It does not issue a broad `pkill python` or terminate unrelated Python applications.

---

## CachyOS / Arch-family setup

RoloDesk itself has no Python package dependencies; Python is only used for the optional loopback server.

```bash
sudo pacman -S --needed python
cd /path/to/RoloDesk_v0.3.4
bash ./run_local.sh
```

RoloDesk prefers LibreWolf/Firefox in ordinary Linux local-server mode when available. Chromium-family browsers remain useful for directory binding and installable-PWA capabilities.

### Install an app launcher on KDE/Plasma or another Linux desktop

```bash
bash ./linux_desktop.sh install
```

Remove only the launcher later with:

```bash
bash ./linux_desktop.sh remove
```

The generated launcher stores the release directory path **only on your own machine**. No device path is embedded in the public scripts or exported data.

---

## Windows

You can double-click the standalone HTML or run the local server:

```powershell
.\run_local.ps1
```

Chromium-family browsers can install hosted RoloDesk as a PWA. The browser's normal **Install app** action is the recommended Windows app-like experience.

---

## macOS

Open the standalone HTML, or from Terminal:

```bash
python3 ./rolodesk_local.py serve
```

On current macOS versions, Safari can turn a hosted RoloDesk page into a Dock web app using **Share → Add to Dock**. Chromium-family browsers can also install the hosted PWA.

---

## Android

RoloDesk works as a normal browser app. For full PWA integration, serve the release from a trusted HTTPS origin and install it.

The manifest includes an Android/Chromium **Web Share Target**. On supporting browsers this lets another application share readable text to RoloDesk, where it is staged as a local Note. This is the preferred ColorNote path because it uses Android's normal device Share action instead of attempting to decode ColorNote's proprietary backup format.

For the Google Pixel / Chromium-family path:

1. Open the HTTPS-hosted RoloDesk page.
2. Install/Add it to the device.
3. In ColorNote, choose **Share**.
4. Choose **RoloDesk** if the browser registered it as a share target.

Raw `file://` HTML cannot register itself as an Android share target.

---

## iPhone / iPad

The browser interface and normal file import/export remain usable. A hosted RoloDesk page can be added to the Home Screen as a web app on current iOS/iPadOS.

The Web Share **Target** manifest feature is not currently supported by Safari/iOS, so receiving ColorNote-style OS shares directly is not promised on iPhone/iPad. Use normal import, copy/paste, or files instead.

---

## Native RoloDesk files

### `.rcc`

Human-readable ABI-style JSON when not password-protected.

### `.rdc`

Compact machine-oriented native envelope.

Both preserve the full RoloDesk structure, including deck position and UI preferences.

Password-protected RCC/RDC currently use:

- PBKDF2-SHA-256
- 310,000 iterations
- random 16-byte salt per save
- AES-256-GCM
- random 12-byte IV per save
- authenticated decryption
- compression before encryption

Source-file protection no longer controls export policy. After an unlocked session is open, card/deck/database exports may be intentionally open, password-protected, recipient-locked, or cryptographically signed. Password-containing open exports require an explicit warning/confirmation.

> RoloDesk v0.3.4 is not a professionally audited password manager. File encryption protects data at rest, but an unlocked browser session can still be observed by a compromised OS, browser, extension, screen/clipboard capture, or maliciously modified hosted copy.

---

## Interchange formats

Depending on deck/scope, RoloDesk can import/export common portable formats including:

- CSV / TSV
- XLSX
- ODS / LibreOffice spreadsheets
- ICS / iCalendar
- VCF / vCard
- TXT
- Markdown
- RTF-safe text
- `.script` display text
- RCC / RDC native files

Markdown and script-like note content is displayed as content, not executed. Links remain non-active in the Notes renderer.

---

## Independent export security and RDX

A database password protects the native source snapshot; it does **not** revoke the owner's ability to export unlocked data. Export now has independent choices:

- **Open / unprotected** — standard/native file, including deliberate plaintext exports from a protected source.
- **Password-protected RDX** — AES-256-GCM export with an export-specific password.
- **Recipient public-key RDX** — RSA-OAEP-3072 wraps a random AES-256-GCM content key.
- **ECDSA P-256 signed RDX** — browser-native signature verification with a key fingerprint.
- **SHA-256 receipt** — integrity sidecar; not a signer identity.
- **External BTC / PQC manifest** — exact SHA-256/signing message for external secp256k1, Bitcoin-like, or PQC signing tools.

RDX files can contain any RoloDesk export format and can be imported back into RoloDesk. Recipient and signing private-key files (`.rdkey`) are themselves password-encrypted when generated. Public key files (`.rdpub`) are intended to be shared.

See **CRYPTO_RELEASE_README.md** for the complete workflow.

---

## Storage Home and `rdc.fsl`

Supporting Chromium-family browsers can bind a user-selected directory as **Storage Home**.

RoloDesk may then:

- directly write RCC/RDC snapshots there,
- scan for recognized files,
- remember the directory handle in IndexedDB,
- write encrypted `rdc.fsl` loader metadata,
- auto-resume the last native file while browser permission still exists.

`rdc.fsl` means **RoloDeskController.FirstStartLoader**. It does not contain a magic unrestricted operating-system path and cannot bypass browser sandbox permissions after site data is erased.

---

## Two self-contained link modes

### RoloDesk Link v1

A RoloDesk-native `#rd1...` URL fragment. The fragment contains a compressed snapshot and is decoded locally by RoloDesk. URL fragments are not sent to the ordinary HTTP server request.

When RoloDesk is opened from a normal public HTTPS deployment, generated links reuse that deployment URL. Local/file sessions fall back to the intended GitHub Pages location:

```text
https://digimancer3d.github.io/RoloDesk/RoloDesk_v0.3.4.html#rd1...
```

That fallback becomes live after the RoloDesk repository is published and GitHub Pages is enabled.

### Itty.bitty v2

RoloDesk can also generate a real IB2 self-contained page using:

```text
https://itty.bitty.app/
```

The exported page and snapshot are stored in the URL fragment. Link size still matters; large databases should be shared as files instead.

Whole-database links may include Password cards when the user explicitly chooses that export. RoloDesk warns before an unprotected secret-bearing link; password-protected or recipient-locked RDX payloads are the safer link form.

---

## PWA hosting

The public folder already contains:

```text
manifest.webmanifest
sw.js
rolodesk-192.png
rolodesk-512.png
```

For installation/share-target features, host the folder from HTTPS. A static host such as GitHub Pages is sufficient for the app shell because the service worker handles the installed share-target POST locally after installation.

The standalone HTML remains usable without PWA installation.

---

## PQCZIP release

Every RoloDesk release is intended to include a `.pqcasset` PQCZIP transport plus `PQCZIP_README.md`.

The bundled structural PQCZIP is copy-safe and portable. For the complete DigiMancer3D PQC Scout-Knife/hybrid workflow, use:

https://github.com/DigiMancer3D/PQC-Containers

Then run the included copy-safe bridge:

```bash
PQC_WRAPPER=/path/to/PQC-Containers/pah_wrap_improved.py \
  bash ./build_pqczip_safe.sh
```

RoloDesk always requests **copy-safe / keep-source semantics**. Importing or exporting RoloDesk content must not consume, shred, delete, or rewrite the source file merely because it traveled through a scarcity-capable PQC container.

See **PQCZIP_README.md** for application packaging and **CRYPTO_RELEASE_README.md** for signed/protected data-release workflows.

---

## Public-release privacy rules

The public scripts in this release:

- contain no developer home-directory path,
- contain no developer storage-device path,
- contain no private IP address,
- bind the local server only to `127.0.0.1`,
- derive the release path at runtime,
- do not upload user files,
- do not delete arbitrary Python processes,
- stage copies for PQCZIP creation.

Absolute paths generated by `linux_desktop.sh` are written only into the current user's local desktop launcher at install time; they are not part of exported RoloDesk data or the distributed source.

---

## Public package contents

The release package intentionally stays small:

```text
README.md
PQCZIP_README.md
CRYPTO_RELEASE_README.md
RoloDesk_v0.3.4.html
PQCZIP_RoloDesk_v0.3.4_PUBLIC_STRUCTURAL.pqcasset
build_pqczip_safe.sh
rolodesk_release.py
rolodesk_local.py
run_local.sh
run_local.ps1
linux_desktop.sh
manifest.webmanifest
sw.js
rolodesk-192.png
rolodesk-512.png
```

No test reports, private path maps, generated logs, verification dumps, or development screenshots are included in the public archive.

---

## Project status

RoloDesk `0.3.4` is a public-release update to the `0.3.3` baseline, adding independent export security and cryptographic-release workflows. It remains experimental software, especially for password-vault use and browser filesystem integration.

No standalone software license is added by this package. Add the project's intended license at repository level before inviting third-party redistribution or modification under specific terms.
