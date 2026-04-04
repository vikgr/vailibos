# 🤖 AI Context: Vailib Project (v4.1 — April 2026)

**ATTENTION ASSISTANT**: You are continuing development of **Vailib**, a modernized digital library system built on SOPDS. Read this document fully before proceeding.

---

## 📁 Environment & Credentials
- **Root Repository**: `C:\Users\vik\Documents\devops\vailib\` — THE CANONICAL SOURCE OF TRUTH.
- **Remote Host**: `hproliant` (192.168.31.115). User: `vik`.
- **Credentials**: Read `C:\Users\vik\Documents\devops\vailib\secrets.txt` for the sudo password and GitHub PAT. **DO NOT PUSH THIS FILE.**
- **GitHub**: `https://github.com/vikgr/vailib` — `main` branch.
- **Running Container**: `sopds` (on hproliant).
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
- `sudo docker restart sopds`

The `sopds-docker-compose.yml` binds these paths from `/home/vik/vailib/` directly into the container (no `/tmp/` anymore):
- `static/custom/` → `/sopds/static/custom/`
- `templates/` → `/sopds/templates/`
- `modern.css` → `/sopds/opds_catalog/static/sopds/modern.css`
- `models.py`, `views.py` → `/sopds/opds_catalog/`
- Plus `write_middleware.py`, `patch_settings.py` etc.

---

## 🎨 Theme System

Two themes controlled by `data-theme` on `<html>`:
- **`premium` (OLED)**: Dark sidebar layout, deep indigo/violet palette, glassmorphism, Inter font.
- **`eink` (E-Ink)**: Pure monochrome, columnar layout, no animations, serif-friendly, Kindle-safe.

Theme toggle is saved to `localStorage` and persists across sessions.

---

## 🛠️ Admin UI (Constance Config Page)

The Django admin at `/admin/constance/config/` has a complete premium dark theme (`static/custom/css/admin_theme.css`) and full JS enhancement suite (`templates/admin/base.html`). All three phases are complete as of 2026-04-04:

| Phase | Features | Status |
|-------|----------|--------|
| A (CSS) | Toggle switches, single-line path fields, sticky save bar, section styling | ✅ Done |
| B (JS Core) | Collapsible sections, jump nav, ext chips, token masking, cron summary, lang preview, search, unsaved warning, modified highlights | ✅ Done |
| C (Advanced) | Cron presets dropdown, reset confirmation popover, Telegram bot status badge | ✅ Done |

---

## ✅ Completed Milestones (All Phases)

### Phase 1–2 (Early 2026)
- **Dual-Theme UI Engine**: Premium OLED + E-Ink with `data-theme` switching.
- **Custom Flexbox Layout**: Sidebar/main-content architecture replacing legacy Foundation grid.
- **Translation Engine**: 11-language support (EN, RU, DE, EL, ES, FR, AR, HI, PT, ZH, BN).
- **Breadcrumb Translation**: Dynamic breadcrumb strings rendered in active language.
- **Security**: Auth enforcement on all routes via custom middleware.

### Phase 3 (March 2026)
- **GitHub Repository**: Pushed to `https://github.com/vikgr/vailib`.
- **Git-Based Deployment**: Replaced `/tmp/` bind-mount model with `deploy.sh` + git pull.
- **Language Indexing**: Expanded `LangCodes` in `models.py` for Greek, Arabic, Devanagari, Bengali, CJK.
- **Book Download Filenames**: Fixed download to return clean, human-readable filenames.
- **Footer/Sidebar Refactor**: Removed footer on E-Ink, merged stats into Premium sidebar.
- **E-Ink Breadcrumbs**: Clickable breadcrumbs + download buttons on E-Ink book cards.
- **Logos**: Color + E-Ink SVG logos integrated.
- **Language Choices in Admin**: All 11 SOPDS_LANGUAGE options wired into constance via `patch_settings.py`.

### Phase 4 (April 2026)
- **Premium Admin Theme**: Full dark indigo/violet Django admin with `admin_theme.css`.
- **Settings Page Enhancement — Phase A+B+C**: All 14 features implemented (see table above).

---

## 📋 NEXT SESSION PRIORITIES

1. **Deploy Phase C to server**: Run `bash /home/vik/vailib/deploy.sh` on hproliant to make Phase C live.
2. **Container Merger**: Build the `vailib:latest` Docker image (from `docker/`) that compiles everything natively — eliminating all bind-mounts entirely.
3. **Converter Bot Integration**: Verify the Telegram bot drops files into `/library` and triggers a re-scan.
4. **Auto-Scan Hook**: Trigger `sopds_scanner` whenever the bot finishes a conversion.
5. **Kindle Stress Test**: Verify absolute 1-bit rendering on a physical Kindle/Kobo.

---

## 👾 Resuming Work

Access `secrets.txt` for deployment credentials. The repository is clean and fully pushed. Run `deploy.sh` on hproliant to pick up any local changes pushed since the last deployment.
