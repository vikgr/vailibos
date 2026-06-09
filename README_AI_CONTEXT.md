# 🤖 AI Context: Vailib Project (v4.3 — June 9, 2026)

**ATTENTION ASSISTANT**: You are continuing development of **Vailib**, a modernized digital library system built on SOPDS. Read this document fully before proceeding.

---

## 📁 Environment & Credentials
- **Root Repository**: `C:\Users\vik\Documents\devops\vailib\` — THE CANONICAL SOURCE OF TRUTH.
- **Remote Host**: `hproliant` (192.168.31.115). User: `vik`.
- **Credentials**: Read `C:\Users\vik\Documents\devops\vailib\secrets.txt` for the sudo password and GitHub PAT. **DO NOT PUSH THIS FILE.**
- **GitHub**: `https://github.com/vikgr/vailib` — `main` branch.
- **Running Container**: `vailib` (on hproliant). *Note: `deploy.sh` was updated to restart `vailib` instead of `sopds`.*
- **Library Mount**: `/library` (shared Docker volume).

---

## 🚀 Deployment Architecture (Current — Git-Based)

The old `/tmp/sopds_custom/` bind-mount model has been **replaced**. The current deployment flow is:

1. Edit files locally in `C:\Users\vik\Documents\devops\vailib\`.
2. `git push` to GitHub (`main` branch).
3. SSH into hproliant → run `bash /home/vik/vailib/deploy.sh`.

`deploy.sh` does:
- `git pull origin main` (in `/home/vik/vailib/`)
- Runs `write_middleware.py` (regenerates custom middleware)
- Runs `patch_settings.py` (patches constance language choices into Django settings)
- Copies `sopds-docker-compose.yml` → `/DATA/AppData/sopds/docker-compose.yml`
- `sudo docker restart vailib` (formerly `sopds`)

---

## 🎨 Theme System

Two themes controlled by `data-theme` on `<html>`:
- **`premium` (OLED)**: Dark sidebar layout, deep indigo/violet palette, glassmorphism, Inter font.
- **`eink` (E-Ink)**: Pure monochrome, columnar layout, no animations, serif-friendly, Kindle-safe.

---

## 🛠️ Admin UI (Constance Config Page)
The Django admin at `/admin/constance/config/` has been **completely rebuilt** using a native template override.
- **SaaS Row Layout**: Horizontal rows (label left, control right) with a sticky save bar.
- **Obsidian Velvet Theme**: High-contrast professional dark palette.
- **Status (April 22)**: Verified live and functional on `hproliant`. Aggressive caching issues resolved.

---

## ✅ Completed Milestones

### Phase 1–3
- Dual-theme engine, 11-language support, Breadcrumb translation, Git-based deployment.

### Phase 4 (April 2026)
- **Frontend Theme Segmented Control**: Migrated legacy toggle button to modern premium pill-switch.
- **Admin UI Overhaul**: Replaced Django settings `<table>` structure with native CSS Grid row-based layout.
- **Admin CSS Pro Theme**: Implemented high-contrast professional GitHub-dark palette in `admin_theme.css`.
- **Deployment Verification**: Successfully deployed to `hproliant` and verified via browser.

### Phase 5 (June 2026)
- **Online EPUB Reader Fixes**: Wrapped jQuery/Foundation conflicts in IIFE, implemented ArrayBuffer ZIP parsing, and forced single-column layout flow.

### Phase 6 (June 2026)
- **Aggregated Language Sorting**: Grouped DB lang variants, mapped standard codes, and fixed display overflow on cards.

---

## 📋 NEXT SESSION PRIORITIES

1. **Kindle Stress Test**: Verify absolute 1-bit rendering on a physical Kindle/Kobo.
2. **Auto-Scan Hook Verification**: Ensure scanner detects files converted by bot instantly.

---

## 👾 Resuming Work

Access `secrets.txt` for deployment credentials. The repository is clean and fully pushed. Run `deploy.sh` on hproliant to pick up any local changes pushed since the last deployment.

