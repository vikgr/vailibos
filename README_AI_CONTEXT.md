# 🤖 AI Context: Vailib Project (v5.0 — September 30, 2026)

**ATTENTION ASSISTANT**: You are continuing development of **Vailib**, a modernized digital library system built on SOPDS. Read this document fully before proceeding.

---

## 📁 Environment & Credentials
- **Root Repository**: `C:\Users\vik\Documents\devops\vailib\` — THE CANONICAL SOURCE OF TRUTH.
- **Remote Host**: `hproliant` (`192.168.31.115`). User: `vik`, SSH Key: `C:\Users\vik\.ssh\id_ed25519`.
- **Credentials**: Sudo password `1j2k3l`. Check `secrets.txt` for GitHub PAT. **DO NOT PUSH secrets.txt.**
- **Git Remotes**:
  - `origin`: `https://github.com/vikgr/vailib.git` (GitHub `main` branch).
  - `prod`: `ssh://vik@192.168.31.115/home/vik/vailib` (production server `main` branch).
- **Active Container**: `vailib` running on host `hproliant` port `8081` (`0.0.0.0:8081->8001/tcp`).
- **Database Container**: `library-db` (Postgres 13 alpine).
- **Library Mount**: `/library` (mapped to host book collection).

---

## 🚀 Deployment Architecture (Unified v5.0)

All core daemons (Web, Scanner Watcher, Telegram Bot Assistant, Auto Converter) run inside the single `vailib` Debian-based container.

### Deployment Workflow:
1. Make changes locally in `C:\Users\vik\Documents\devops\vailib\`.
2. Commit locally: `git commit -am "Description"`.
3. Push to both remotes:
   ```bash
   git push origin main
   git push prod main
   ```
4. Apply changes on `hproliant`:
   ```bash
   ssh -i C:\Users\vik\.ssh\id_ed25519 vik@192.168.31.115 "cd /home/vik/vailib && git checkout -f main && echo 1j2k3l | sudo -S docker cp templates/. vailib:/sopds/sopds_web_backend/templates/ && echo 1j2k3l | sudo -S docker cp views.py vailib:/sopds/sopds_web_backend/views.py && echo 1j2k3l | sudo -S docker cp urls.py vailib:/sopds/sopds_web_backend/urls.py && echo 1j2k3l | sudo -S docker restart vailib"
   ```

---

## 🎨 Dual-Identity Theme & Hardware Detection
- Two core themes: `premium` (OLED Dark) and `eink` (monochrome 1-bit zero-JS).
- **Multi-layer auto-detection**:
  - Server middleware (`VailibThemeMiddleware` in `middleware.py`): Checks `User-Agent` against comprehensive e-reader signature list (`kindle`, `kobo`, `pocketbook`, `nook`, `boox`, `tolino`, etc.).
  - Client-side auto-switch (`templates/sopds_main.html`): Checks `screen.colorDepth <= 8` and `window.matchMedia('(monochrome)')` vs effective screen resolution (`Math.max(w,h) * dpr >= 800`).
  - High-res color devices (desktops, iPhones, iPads, Android) default to COLOR.
  - Dedicated e-readers default to E-INK.
  - User manual toggle (`COLOR` / `E-INK` in top nav) is permanently preserved in cookie `vailib_theme` and `localStorage`.

---

## 📖 Universal In-Browser Reader (`/web/read/<id>/`)
- Formats supported: **EPUB** (ePub.js), **PDF** (PDF.js), **FB2** (native XML DOM parser with scroll progress), and **DjVu** (DjVu.js).
- **Keyboard Navigation**:
  - Next Page: `Right Arrow` (`→`), `Page Down`, `Space` (without Shift), `Down Arrow` (`↓`).
  - Previous Page: `Left Arrow` (`←`), `Page Up`, `Shift + Space`, `Up Arrow` (`↑`).
  - ePub iframe penetration: hooks registered on both `window` and `rendition.hooks.content`.
  - Form input and settings drawer bypass to prevent unintended page turns while typing.
- Reading drawer: Dark, Light, Sepia, E-Ink themes, font sizing (12-28px), and font families.

---

## 📤 Manual Book & ZIP Archive Upload (`/web/populate/`)
- Browser-based multi-file upload with drag-and-drop dropzone at `/web/populate/`.
- Supported extensions: `.epub`, `.pdf`, `.fb2`, `.mobi`, `.djvu`, `.cbr`, `.cbz`, `.azw`, `.azw3`, `.txt`, `.doc`, `.docx`, `.rtf`, `.chm`, `.zip`.
- **Smart ZIP Handling**:
  - Auto-extract enabled by default: extracts books from archives into library folder (with Zip Slip path traversal security).
  - Preserves `.fb2.zip` archives natively.
  - Allows keeping ZIP archives intact for SOPDS's native `SOPDS_ZIPSCAN`.
- **Automatic Scanner Triggering**: Touches `/library/.trigger_scan` on upload; `scanner_watcher.sh` detects it within 5 seconds and starts catalog scan.
- **Upload Size**: `DATA_UPLOAD_MAX_MEMORY_SIZE = 1073741824` (1 GB) with 25 MB in-memory buffer.
- Dual theme support: AJAX progress bar for desktop; standard zero-JS form for e-readers.

---

## 🧙 6-Step Web Setup Wizard (`/web/setup/`)
- First-time setup wizard with clickable/skippable progress indicator dots:
  1. Welcome & Environment
  2. Storage & Directory write tests
  3. Database connection
  4. Admin creation
  5. Telegram Bot configuration
  6. Library populate & bootstrap
- Auto-redirects fresh installs to `/web/setup/` via `SOPDSSetupMiddleware`.

---

## 🤖 Daemons & Automation
- `scanner_watcher.sh`: Polls for `/library/.trigger_scan` every 5 seconds.
- `bot.sh`: Custom Telegram Bot daemon with atomic Constance database config polling.
- `convert.sh`: Calibre and OCR conversion worker.

---

## 🌎 Global Language Matrix (12 Languages)
- English (`en`), Russian (`ru`), German (`de`), Greek (`el`), Spanish (`es`), French (`fr`), Arabic (`ar`), Hindi (`hi`), Portuguese (`pt`), Chinese (`zh-hans`), Bengali (`bn`), Dutch (`nl`).
- Index-aware script classification and flag badges from `flagcdn.com`.

---

## ✅ Completed Milestones
- **Phase 1–6**: Dual-theme UI, 11 languages, admin overhaul, EPUB reader fixes.
- **Phase 7**: Multi-layer hardware & screen resolution auto-detection (COLOR vs E-INK).
- **Phase 8**: Universal reader keyboard navigation across EPUB, PDF, FB2, DjVu.
- **Phase 9**: Manual multi-book & ZIP archive upload with auto-extraction and auto-scan.
- **Phase 10**: 6-Step interactive Setup Wizard with skippable step dots and Telegram Bot integration.
- **Phase 11**: 12-language matrix (Dutch added) and 1 GB upload capacity.

---

## 📋 Resuming Work
All changes are tracked in Git, pushed to `origin/main` (GitHub) and `prod/main` (`hproliant`), and live on the container. Check `task.md` and `walkthrough.md` for complete implementation histories.
