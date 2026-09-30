# 📖 VAILIB: The Ultimate Digital Library & OPDS Ecosystem 🚀

[![GitHub License](https://img.shields.io/github/license/vikgr/vailib)](https://github.com/vikgr/vailib/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-2.1.15-green.svg)](https://www.djangoproject.com/)
[![Languages](https://img.shields.io/badge/languages-12%20matrix-orange.svg)](#-global-language-matrix-12-languages)
[![Docker](https://img.shields.io/badge/docker-unified%20v5.0-blueviolet.svg)](#-quick-start)

**Vailib (v5.0)** is a high-performance, modernized digital library ecosystem. It unifies a powerful **Telegram Document Converter Bot**, a responsive **Web OPDS Catalog** engine, an **Interactive 6-Step Setup Wizard**, a **Universal In-Browser Book Reader** (EPUB, PDF, FB2, DjVu) with keyboard browsing, a **Drag-and-Drop Book & ZIP Archive Uploader**, and an Obsidian-styled **Django Admin Panel** into a single containerized architecture.

Built for book lovers, researchers, and archival enthusiasts, Vailib transforms raw files into a premium, searchable, and globally accessible reading experience across desktops, smartphones, and e-readers.

> [!NOTE]
> **Vailib** is built upon the robust foundation of the [SOPDS](https://github.com/zveronline/sopds) project by **zveronline**. We have re-engineered the platform with a dual-identity responsive UI, hardware-based e-ink auto-detection, multi-format browser reading, ZIP batch extraction, deep 12-language indexing, and unified daemon pipelines.

---

## 🌟 Key Features

### 🎨 1. Intelligent Dual-Identity UI & Hardware Detection
Vailib features an adaptive UI engine that automatically determines the optimal display mode:
- **Premium COLOR Mode (OLED Dark)**: A sleek interface with deep indigo/violet palettes, glassmorphism blur effects, smooth CSS transitions, and OLED optimization for modern desktop browsers, laptops, iPhones, iPads, and Android devices.
- **High-Contrast E-INK Mode**: A pure 1-bit, high-contrast, zero-animation interface engineered for Kindle, Kobo, PocketBook, Nook, Onyx Boox, Remarkable, Tolino, and legacy mobile browsers.
- **Hardware-Aware Auto-Detection**:
  - Automatically serves COLOR to high-DPI color displays based on user-agent, viewport resolution, and color depth.
  - Automatically serves E-INK to dedicated e-reader browsers and monochrome screens.
  - Permanent manual override via the sticky header tab (`COLOR` / `E-INK`) saved to cookies and `localStorage`.

---

### 📖 2. Universal In-Browser Book Reader
Read books directly in your browser without external apps:
- **EPUB**: Rendered via ePub.js with binary stream parsing and isolated iframe scopes.
- **PDF**: Integrated high-resolution canvas rendering powered by PDF.js.
- **FB2**: High-speed native XML DOM parser with automatic section hierarchy, heading formatting, and reading progress calculation.
- **DjVu**: Integrated DjVu.js client-side viewer.
- **Reading Customization Drawer**: Choose between Dark (OLED), Light, Sepia, and E-Ink palettes, scale font sizes from 12px to 28px, and switch typefaces (Serif, Sans, OpenDyslexic, Monospace).

#### ⌨️ Reader Keyboard Navigation Shortcuts
| Action | Supported Keys |
| :--- | :--- |
| **Next Page** | `Right Arrow` (`→`), `Page Down` (`PgDn`), `Space`, `Down Arrow` (`↓`) |
| **Previous Page** | `Left Arrow` (`←`), `Page Up` (`PgUp`), `Shift + Space`, `Up Arrow` (`↑`) |

*Keyboard events seamlessly penetrate EPUB iframe scopes and are automatically disabled when typing in search bars or settings drawers.*

---

### 📤 3. Manual Book & ZIP Archive Upload
Located directly under **Upload & Populate** (`/web/populate/`):
- **Drag-and-Drop & Multi-File Selection**: Drop individual eBooks or bulk collections directly onto the browser dropzone.
- **Supported eBook Formats**: `.epub`, `.pdf`, `.fb2`, `.mobi`, `.djvu`, `.cbr`, `.cbz`, `.azw`, `.azw3`, `.txt`, `.doc`, `.docx`, `.rtf`, `.chm`.
- **Smart ZIP Archive Extraction**:
  - Automatically unpacks `.zip` archives containing dozens of books into your library folder.
  - Recursively discovers books in nested archive folders.
  - Built-in protection against Zip Slip path traversal vulnerabilities.
  - Preserves single-book `.fb2.zip` archives natively.
  - Option to retain ZIP archives intact for SOPDS's native `SOPDS_ZIPSCAN` indexing.
- **Automatic Library Scanner Trigger**: Uploading touches `.trigger_scan`; the background watcher detects new files within 5 seconds and indexes them immediately.
- **1 GB Upload Limit**: Supports large scanned PDF/DjVu volumes and multi-book archives (`DATA_UPLOAD_MAX_MEMORY_SIZE = 1GB`).
- **Dual-Theme Compatibility**: Glassmorphic drag-and-drop UI with upload progress bar for desktop; clean zero-JS multipart form for e-readers.

---

### 🌐 4. Pre-Populate from Online Catalogs
Bootstrap your library with thousands of free eBooks directly from the web interface:
- **Project Gutenberg**: Fetch the most popular public-domain titles across 12 languages.
- **Standard Ebooks**: Curated, beautifully formatted classic literature.
- **Live Dashboard**: Real-time progress bars, transfer percentage counters, language filtering chips, and live execution logs.

---

### 🧙 5. Interactive 6-Step Web Setup Wizard
A frictionless onboarding flow available at `/web/setup/`:
1. **Welcome & Environment Verification**: Verifies paths and permissions.
2. **Directory & Storage Testing**: Runs interactive live write-tests on the `/library` volume.
3. **Database Configuration**: Validates PostgreSQL connectivity.
4. **Admin Account Creation**: Creates your primary superuser.
5. **Telegram Bot Assistant**: Optional token and Chat ID configuration.
6. **Library Bootstrap**: Optional automated pre-population from Gutenberg.
- Features **clickable and skippable progress indicator dots** allowing quick navigation between steps.

---

### 🤖 6. Unified Daemon & Telegram Assistant Bot
Vailib bundles background services directly inside the container:
- **Telegram Bot Daemon**: Send PDFs, DJVUs, or FB2s to your bot; it automatically performs OCR, converts them to EPUB/MOBI, and places them into your library.
- **Live Settings Reload**: Updates to `BOT_TOKEN` or `CHAT_ID` via the admin UI or setup wizard are atomically picked up without container restarts.
- **Scanner Watcher**: Monitors `/library/.trigger_scan` and triggers `sopds_scanner` automatically whenever new books arrive.

---

### 🌎 7. Global Language Matrix (12 Languages)
The entire catalog and UI are fully internationalized and script-aware:
- 🇬🇧 English (`en`)
- 🇷🇺 Russian (`ru`)
- 🇩🇪 German (`de`)
- 🇬🇷 Greek (`el`)
- 🇪🇸 Spanish (`es`)
- 🇫🇷 French (`fr`)
- 🇸🇦 Arabic (`ar`)
- 🇮🇳 Hindi (`hi`)
- 🇵🇹 Portuguese (`pt`)
- 🇨🇳 Chinese Simplified (`zh-hans`)
- 🇧🇩 Bengali (`bn`)
- 🇳🇱 Dutch (`nl`)

Includes dynamic flag badges from `flagcdn.com`, case-insensitive alias normalization, and Unicode script group detection.

---

### 🛠️ 8. Obsidian Velvet Admin Interface
The Django admin panel (`/admin/constance/config/`) features a high-contrast dark theme:
- **SaaS Row Layout**: Horizontal setting cards with persistent collapsible sections.
- **Sticky Save Bar**: Live unsaved-changes counter and save button.
- **Live Status Badges**: Real-time indicators for Telegram bot status (`🟢 Connected` / `🔴 Offline`).
- **Quick-Jump Sidebar & Quick Filter**: Instant fuzzy search across all 35 configuration options.

---

## 🚀 Quick Start

### Option A: Interactive Installer (Recommended)
On your Linux host or server:
```bash
git clone https://github.com/vikgr/vailib.git
cd vailib
chmod +x install.sh
sudo ./install.sh
```
The installer prompts for book storage paths, database credentials, and port bindings, then spins up the unified container stack.

---

### Option B: Docker Compose
Create a `docker-compose.yml`:
```yaml
services:
  db:
    image: postgres:13-alpine
    container_name: library-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: sopds
      POSTGRES_USER: sopds
      POSTGRES_PASSWORD: changeme
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    networks:
      - library-net

  sopds:
    image: ghcr.io/vikgr/vailib:latest # Or build locally from Dockerfile_vailib
    container_name: vailib
    restart: unless-stopped
    depends_on:
      - db
    environment:
      DB_HOST: db
      DB_NAME: sopds
      DB_USER: sopds
      DB_PASS: changeme
      DB_PORT: "5432"
      SOPDS_ROOT_LIB: /library
      TIME_ZONE: Europe/Madrid
    ports:
      - "8081:8001"
    volumes:
      - ./data/sopds:/var/lib/sopds
      - /path/to/your/books:/library
    networks:
      - library-net

networks:
  library-net:
    name: vailib_network
```

Run:
```bash
docker compose up -d
```
Visit `http://localhost:8081/web/` to begin the 6-step setup wizard!

---

## 📁 Repository Structure

| File / Folder | Purpose |
| :--- | :--- |
| `Dockerfile_vailib` | Multi-stage unified container build (Python 3.10, Calibre, DjVuLibre, OCR) |
| `install.sh` | Interactive CLI installation wizard |
| `deploy.sh` | Zero-downtime remote deployment script |
| `views.py` | Core Django views: UploadView, PopulateView, ReaderView, SetupWizardView |
| `urls.py` | Web catalog routing definitions |
| `scanner_watcher.sh` | Background watcher detecting `.trigger_scan` events |
| `bot.sh` | Telegram assistant bot daemon with atomic configuration polling |
| `convert.sh` | Automated Calibre/OCR conversion pipeline |
| `download_popular_books.py` | Project Gutenberg & Standard Ebooks crawler |
| `patch_settings.py` | Settings patcher for 12-language matrix and 1GB upload limits |
| `templates/` | Dual-theme templates (Modern OLED + E-Ink Zero-JS) |
| `static/custom/` | Modern UI styles (`modern.css`), themes, and admin stylesheet |

---

## 🤝 Contributing

Contributions, feature requests, and bug reports are welcome!
Feel free to open an issue or submit a pull request on [GitHub](https://github.com/vikgr/vailib).

---

## ⚖️ Credits & License

- **License**: GNU General Public License v3.0 ([GPL-3.0](LICENSE)).
- **Foundation**: Based on [SOPDS](https://github.com/zveronline/sopds) by **zveronline**.
- **Modernization & Architecture**: Engineered by **vikgr**.
