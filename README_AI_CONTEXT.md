# 🤖 AI Context: The Unified Vailib Project (v4.0)

**ATTENTION ASSISTANT**: If you are reading this, continue the development of **Vailib**, a unified digital library system. This project merges a custom Telegram Doc Converter Bot with a heavily modified SOPDS catalog, now branded natively as **Vailib**.

---

## 📁 Environment & Credentials
- **Root Repository**: `C:\Users\vik\Documents\devops\vailib\` — THIS IS THE CANONICAL SOURCE.
- **Remote Host**: `hproliant` (192.168.31.115). User: `vik`. 
- **Credentials**: Read the local `C:\Users\vik\Documents\devops\vailib\secrets.txt` for the sudo password and GitHub PAT. **DO NOT PUSH THIS FILE.**
- **Container**: `sopds` (to be renamed to `vailib` in next container rebuild).
- **Library Mount**: Shared volume at `/library`.

---

## 🚀 Deployment Overview (Legacy vs. Modern)

### 🔴 Legacy Mode (Current Active Server)
Currently, the server uses a `sopds-docker-compose.yml` with massive volume bind-mounts pointing to `/tmp/sopds_custom/`. Use `scp` to move local changes to the server and update the `/tmp/` files manually.

### 🟢 Modern Mode (Ready for Deployment)
The `vailib/docker/` directory contains a **Zero-Bind Dockerfile**. 
- It compiles all `modern.css`, `views.py`, and templates natively into the image.
- Build command: `docker build -t vailib:latest .` from the `docker/` folder.
- Deployment Goal: Move to the unified `vailib` image and delete all the old `/tmp/` bind-mounts.

---

## 🎨 Theme System (modern.css)
Two themes controlled via `data-theme` attribute on `<html>`:
- **`premium` (OLED)**: Dark sidebar layout, golden "Cyber-Cat" logo.
- **`eink` (E-Ink)**: Pure monochrome, top-bar layout, no animations, serif font stack.

---

## ✅ Completed Milestones (Phase 4 — March 2026)
- **11-Language Engine**: Full UI translation (EN, RU, DE, EL, ES, FR, AR, HI, PT, ZH).
- **GitHub Repository**: Project push successful to `https://github.com/vikgr/vailib`.
- **Global Breadcrumb Patch**: Fixed search-type strings (Search by series, etc.) in breadcrumbs.
- **Vailib Branding**: All "SOPDS" terminology scrubbed from the `docker/` build context.
- **Security Check**: `.gitignore` implemented; all passwords scrubbed from public docs.

---

## 🤖 NEXT SESSION PRIORITIES 
1. **The Container Merger**: Build the `vailib:latest` image and verify it runs flawlessly without any `/tmp/` bind-mounts.
2. **Converter Bot Integration**: Ensure the Telegram Bot is correctly dropping files into the `/library` volume and that Vailib can scan them instantly.
3. **Auto-Scan Hook**: Potentially trigger a catalog scan whenever the bot finishes a conversion.
4. **Hardware Stress Test**: Verify absolute 1-bit monochromatization on a physical Kindle/Kobo device.

---

## 👾 Resuming Work
The session is cleanly parked. Access the `secrets.txt` for deployment and proceed with **Step 1: Building the Unified Image**.
