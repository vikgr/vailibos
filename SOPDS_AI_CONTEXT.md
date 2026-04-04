# AI Context: SOPDS / Vailib (v4.1 — April 2026)

> **Superseded** — For the full, authoritative AI context see `README_AI_CONTEXT.md`.  
> This file is kept for historical reference only.

---

## 🌐 Overview
SOPDS is the web and OPDS engine at the core of Vailib. It has been fully modernized into a dual-theme catalog (Premium OLED + E-Ink) with a premium admin interface, 11-language support, and a git-based deployment pipeline.

---

## ⚙️ Configuration (Current State — April 2026)
- **Host**: `hproliant` (192.168.31.115). User: `vik`.
- **Image**: `zveronline/sopds:latest` (Django-based, with Vailib bind-mounts)
- **Database**: Postgres 13 (Container: `sopds-db`)
- **Library Path**: `/library`
- **Deployment**: `bash /home/vik/vailib/deploy.sh` (git pull → docker restart)

> ⚠️ The old `/tmp/sopds_custom/` SCP bind-mount model is **retired**. Do not use it.

---

## 🚀 Current Deployment Model
Files in `/home/vik/vailib/` are bind-mounted directly into the `sopds` container via `sopds-docker-compose.yml`. Changes are propagated by:
1. `git push` from the local Windows workstation
2. `bash /home/vik/vailib/deploy.sh` on hproliant

---

## 🎨 UI Architecture
- **`modern.css`**: Core dual-theme CSS. `[data-theme="premium"]` = dark sidebar layout. `[data-theme="eink"]` = columnar monochrome layout.
- **`static/custom/css/admin_theme.css`**: Full 1 300-line dark admin theme.
- **`templates/admin/base.html`**: 14-feature JS enhancement suite for the constance settings page.
- Theme choice persisted in `localStorage`.

---

## ✅ All Phases Complete
See `UI_UPGRADE_WALKTHROUGH.md` for the full history. As of 2026-04-04, Phases 1–4 (including admin Phase A+B+C) are complete and pushed to GitHub.
