# 📖 VAILIB: The Ultimate Digital Library 🚀

[![GitHub License](https://img.shields.io/github/license/vikgr/vailib)](https://github.com/vikgr/vailib/blob/main/LICENSE)
[![Docker Image](https://img.shields.io/docker/pulls/zveronline/vailib)](https://hub.docker.com/r/zveronline/vailib)

**Vailib** (v4.1) is a high-performance, modernized digital library ecosystem. It combines a powerful **Telegram Document Converter Bot** with a gorgeous, responsive **Web OPDS Catalog** engine and a fully themed **Django admin panel**.

Built for book lovers, researchers, and archival enthusiasts, Vailib transforms a raw collection of files into a premium, searchable, and globally accessible library experience.

> [!NOTE]
> **Vailib** is built on the robust foundation of the [SOPDS](https://github.com/zveronline/sopds) project by **zveronline**. We have extended the core engine with a completely new UI, deep internationalization, a premium admin theme, and integrated document processing pipelines.

---

## 🌟 Key Features

### 🎨 Dual-Identity UI Engine
Vailib features a revolutionary theme engine that adapts to any device:
- **Premium Dark Mode**: A sleek, modern interface with deep indigo/violet accents, glassmorphism effects, CSS transitions, and an OLED-optimized layout.
- **High-Efficiency E-Ink Mode**: A pure 1-bit, high-contrast, zero-animation interface specifically engineered for Kindle, Remarkable, and older e-readers.

### 🛠️ Premium Admin Interface
The Django admin panel is fully reskinned with a dark premium theme and a rich settings UX:
- **Collapsible sections** with chevron toggles and `localStorage` persistence
- **Sticky save bar** with unsaved-changes counter
- **Quick-jump sidebar** navigation
- **iOS-style toggle switches** for all boolean settings
- **Cron preset dropdown** — one-click schedule configuration
- **Telegram bot status badge** — live connection check (`🟢 Connected` / `🔴 Offline`)
- **Reset-to-default confirmation popover** — prevents accidental field resets
- **Quick search** — filter all 35 settings by name (Ctrl+F hijacked)
- **Token masking** — Telegram API token hidden by default with Show/Hide toggle

### 🌎 Global Language Matrix (11 languages)
The entire library interface is fully translated and index-aware:
- 🇬🇧 English | 🇷🇺 Russian | 🇩🇪 German | 🇬🇷 Greek | 🇪🇸 Spanish | 🇫🇷 French
- 🇸🇦 Arabic | 🇮🇳 Hindi | 🇵🇹 Portuguese | 🇨🇳 Chinese (Simplified) | 🇧🇩 Bengali

Book indexing covers all 11 Unicode script groups including CJK auto-detection.

### 🤖 Automatic Document Pipeline
Integrated **Telegram Converter Bot** support:
- Upload any **PDF** or **DJVU** via Telegram.
- **OCR Integration**: Automatically performs OCR on image-only documents.
- **Auto-Cataloging**: Converted documents are instantly saved to the library volume and indexed for the web catalog.

### ⚡ Git-Based Deployment
Vailib uses a clean git-pull deployment model:
- Edit locally → `git push` to GitHub → `bash deploy.sh` on the server.
- No manual SCP, no `/tmp/` staging directories.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/vikgr/vailib.git
cd vailib
```

### 2. Build the Docker Image
Navigate to the [docker](./docker) directory for detailed build instructions:
```bash
cd docker
docker build -t vailib:latest .
```

### 3. Launch with Docker Compose
```yaml
services:
  vailib:
    image: vailib:latest
    container_name: vailib
    ports:
      - "8001:8001"
    volumes:
      - /your/library/path:/library:ro
      - vailib_db:/var/lib/postgresql/data
volumes:
  vailib_db:
```

---

## 📁 Project Structure

| Path | Purpose |
|------|---------|
| `docker/` | Dockerfile and native image build (zero bind-mounts) |
| `templates/` | Overhauled Django templates for both catalog and admin |
| `templates/admin/base.html` | Admin base template with full Phase A–C JS enhancements |
| `static/custom/css/admin_theme.css` | Premium dark admin theme (1 300+ lines) |
| `modern.css` | Core dual-theme CSS for the catalog UI |
| `views.py` | Enhanced backend: breadcrumbs, download filenames, language routing |
| `models.py` | Expanded `LangCodes` for 11-script indexing |
| `deploy.sh` | One-command deployment script (git pull + docker restart) |
| `patch_settings.py` | Injects SOPDS_LANGUAGE choices into Django settings at deploy time |
| `write_middleware.py` | Regenerates custom auth middleware at deploy time |
| `sopds-docker-compose.yml` | Production compose file with bind-mounts from `/home/vik/vailib/` |

---

## 🤝 Contributing
Vailib is an open-source project. Contributions, bug reports, and feature requests are welcome!

**GitHub Repository**: [https://github.com/vikgr/vailib](https://github.com/vikgr/vailib)

---

## ⚖️ Credits & License
Vailib is licensed under the GPL-3.0 License.

**Foundation**: Based on [SOPDS](https://github.com/zveronline/sopds) by **zveronline**.  
**Development**: Engineered by **vikgr**.
