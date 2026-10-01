# 📖 VAILIB (vailibos) — The Ultimate Modern Digital Library 🚀

[![GitHub License](https://img.shields.io/github/license/vikgr/vailibos)](https://github.com/vikgr/vailibos/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-2.1.15-green.svg)](https://www.djangoproject.com/)
[![Languages](https://img.shields.io/badge/languages-12%20matrix-orange.svg)](#-12-language-global-matrix)
[![Docker](https://img.shields.io/badge/docker-ready%20v5.0-blueviolet.svg)](#-quick-start)
[![Architecture](https://img.shields.io/badge/architecture-unified%20container-success.svg)](#-unified-container-architecture)

<p align="center">
  <img src="docs/images/vailib_showcase.jpg" alt="Vailib v5.0 Showcase: OLED Dark Mode and E-Ink Dual Identity Reader" width="100%" style="border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.5);">
</p>

**Vailib (vailibos)** is an all-in-one, high-performance digital library and OPDS catalog ecosystem. It unites a **Universal In-Browser eBook Reader** (EPUB, PDF, FB2, DjVu) with keyboard navigation, **Drag-and-Drop Book & ZIP Archive Uploading**, **Hardware-Aware E-Ink Auto-Detection**, an **Interactive 6-Step Web Setup Wizard**, an **Automated Telegram OCR/Conversion Bot**, and a Dark Obsidian **Admin Panel** into a single, effortless Docker deployment.

Built for book collectors, researchers, and self-hosters, Vailib turns any collection of files into a beautifully organized, searchable, and globally accessible private library.

---

## ⚡ Quick Start in 60 Seconds

### Method 1: Universal 1-Line Installer (Recommended)
Works on any Linux server, VPS, Raspberry Pi, or macOS with Docker:
```bash
curl -fsSL https://raw.githubusercontent.com/vikgr/vailibos/main/install.sh | bash
```
The wizard checks dependencies, configures your preferred port and book paths, sets up storage, and boots the entire stack automatically.

---

### Method 2: Docker Compose (3 Steps)
If you prefer running via standard Docker Compose:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vikgr/vailibos.git
   cd vailibos
   ```

2. **Configure your environment (optional):**
   ```bash
   cp .env.example .env
   ```
   *(By default, `.env.example` is pre-configured to store books in `./books` and run on port `8081`)*

3. **Launch the stack:**
   ```bash
   docker compose up -d
   ```

4. **Access your library:**
   Open **`http://<your-server-ip>:8081/web/setup/`** in your web browser to finish the 6-step setup wizard!

---

## 🌟 Core Features & Highlights

### 🎨 1. Intelligent Dual-Identity UI & Hardware Auto-Detection
Vailib features an adaptive UI engine that tailors the interface to the device you are using:
- **Premium COLOR Theme (OLED Dark)**: Glassmorphism blur panels, deep indigo/violet palette, glowing accents, and smooth transitions optimized for desktop monitors, laptops, iPhones, iPads, and modern Android devices.
- **Pure 1-Bit E-INK Theme**: High-contrast, zero-animation, zero-JS layout specifically crafted for Kindle, Kobo, PocketBook, Nook, Onyx Boox, Remarkable, and Tolino e-readers.
- **Automatic Display Detection**:
  - Automatically identifies e-readers via User-Agent and serves the high-contrast E-Ink interface.
  - Automatically identifies high-resolution color screens via viewport resolution and color depth.
  - Permanent manual override switch (`COLOR` / `E-INK`) in the top navigation bar, saved to cookies and `localStorage`.

---

### 📖 2. Universal In-Browser Book Reader
Read any book format directly inside your browser without installing third-party apps:
- **EPUB**: Rendered via ePub.js with binary stream decoding and clean single-column pagination.
- **PDF**: High-resolution canvas rendering powered by PDF.js with instant page jumps.
- **FB2**: High-speed native XML DOM parser with section hierarchy formatting and scroll progress tracking.
- **DjVu**: Integrated DjVu.js client-side viewer.
- **Reading Drawer**: Customize font sizes (12px to 28px), select typefaces (Serif, Sans-Serif, OpenDyslexic, Monospace), and switch reading palettes (OLED Dark, Light, Sepia, E-Ink).

#### ⌨️ Reader Keyboard Navigation Shortcuts
| Action | Supported Keyboard Keys |
| :--- | :--- |
| **Next Page** | `Right Arrow` (`→`), `Page Down` (`PgDn`), `Space`, `Down Arrow` (`↓`) |
| **Previous Page** | `Left Arrow` (`←`), `Page Up` (`PgUp`), `Shift + Space`, `Up Arrow` (`↑`) |

*Keyboard navigation effortlessly penetrates EPUB iframe scopes and automatically disables when typing in form fields or settings drawers.*

---

### 📤 3. Manual Book & ZIP Archive Upload
Located under **Upload & Populate** (`/web/populate/`):
- **Drag-and-Drop & Multi-File Picker**: Drop individual books or multiple files at once.
- **Supported File Types**: `.epub`, `.pdf`, `.fb2`, `.mobi`, `.djvu`, `.cbr`, `.cbz`, `.azw`, `.azw3`, `.txt`, `.doc`, `.docx`, `.rtf`, `.chm`, and `.zip`.
- **Smart ZIP Extraction**:
  - Automatically unpacks ZIP archives containing dozens of books into your library folder.
  - Recursively finds and extracts books from nested folders.
  - Built-in Zip Slip protection against directory traversal attacks.
  - Single-book `.fb2.zip` archives are recognized and preserved natively.
  - Option to retain ZIP archives intact for SOPDS's native `SOPDS_ZIPSCAN` engine.
- **Instant Background Scan**: Uploading automatically touches `.trigger_scan`, prompting the catalog scanner to index newly added books within 5 seconds.
- **High Capacity**: Supports large scanned PDF/DjVu documents and archives up to 1 GB (`DATA_UPLOAD_MAX_MEMORY_SIZE = 1GB`).

---

### 🌐 4. Pre-Populate from Online Catalogs
Bootstrap your digital library with thousands of free eBooks directly from the web interface:
- **Project Gutenberg**: Fetch top public-domain books across 12 languages.
- **Standard Ebooks**: Curated, beautifully typeset editions of classic literature.
- **Live Progress Monitor**: Real-time progress bar, percentage counters, language chips, and live logs.

---

### 🧙 5. Interactive 6-Step Web Setup Wizard
A frictionless first-run onboarding experience available at `/web/setup/`:
1. **Welcome & Environment Verification**: Verifies host paths and permissions.
2. **Directory & Storage Testing**: Runs interactive live write-tests on the `/library` volume.
3. **Database Setup**: Connects and verifies PostgreSQL database tables.
4. **Administrator Account**: Creates the primary superuser account.
5. **Telegram Bot Assistant**: Configures bot token and allowed chat ID (optional).
6. **Library Bootstrap**: Pre-populates popular books from Project Gutenberg.
- Features **clickable and skippable progress indicator dots** allowing quick navigation between steps.

---

### 🤖 6. Unified Container Architecture & Telegram Bot
Vailib runs all required services inside a single container:
- **Web & OPDS Server**: Serves standard web UI and OPDS feeds for mobile readers (KyBook, Moon+ Reader, FBReader, Aldiko, etc.).
- **Scanner Watcher**: Real-time file watcher detecting `.trigger_scan` triggers.
- **Telegram Document Bot**: Send any PDF, FB2, or DjVu document to your Telegram bot; it automatically executes OCR, converts to EPUB, and stores the book in your library.
- **Atomic Config Reloading**: Changes to bot credentials in the admin panel or setup wizard are picked up dynamically without restarting containers.

---

### 🌎 7. 12-Language Global Matrix
The entire library catalog and user interface are internationalized:
- 🇬🇧 **English** (`en`)
- 🇷🇺 **Russian** (`ru`)
- 🇩🇪 **German** (`de`)
- 🇬🇷 **Greek** (`el`)
- 🇪🇸 **Spanish** (`es`)
- 🇫🇷 **French** (`fr`)
- 🇸🇦 **Arabic** (`ar`)
- 🇮🇳 **Hindi** (`hi`)
- 🇵🇹 **Portuguese** (`pt`)
- 🇨🇳 **Chinese Simplified** (`zh-hans`)
- 🇧🇩 **Bengali** (`bn`)
- 🇳🇱 **Dutch** (`nl`)

Includes Unicode script group classification and country flag badges from `flagcdn.com`.

---

### 🛠️ 8. Obsidian Dark Admin Panel
The Django admin panel (`/admin/constance/config/`) has been redesigned:
- **SaaS Row Layout**: Horizontal setting cards with collapsible accordion sections.
- **Sticky Save Bar**: Unsaved changes counter and persistent save trigger.
- **Live Connection Badges**: Real-time Telegram bot connection status (`🟢 Connected` / `🔴 Offline`).
- **Instant Search**: Quick fuzzy filter across all 35 settings.

---

## ⚙️ Configuration Reference

All settings can be customized in your `.env` file or directly via the Web Setup Wizard:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `8081` | Host port mapped to the web interface and OPDS feed. |
| `BOOKS_PATH` | `./books` | Host directory where your eBook collection is stored. |
| `DATA_PATH` | `./data/sopds` | Host directory for application cache and user metadata. |
| `DB_DATA_PATH` | `./data/postgres` | Host directory for PostgreSQL database storage. |
| `POSTGRES_USER` | `sopds` | PostgreSQL database user name. |
| `POSTGRES_DB` | `sopds` | PostgreSQL database name. |
| `DB_PASSWORD` | `vailib_secure_password` | Database user password. |
| `TIME_ZONE` | `Europe/Madrid` | Server timezone for scheduled catalog scans. |
| `BOT_TOKEN` | *(empty)* | Optional Telegram Bot API token from `@BotFather`. |
| `CHAT_ID` | *(empty)* | Optional Telegram Chat ID authorized to manage the bot. |

---

## 🔒 Reverse Proxy & HTTPS Configuration

To expose Vailib over HTTPS on your domain (e.g., `books.example.com`):

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name books.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name books.example.com;

    ssl_certificate /etc/letsencrypt/live/books.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/books.example.com/privkey.pem;

    # Allow large book and archive uploads (1GB)
    client_max_body_size 1024M;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket & streaming support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Caddyfile Configuration
```caddy
books.example.com {
    request_body {
        max_size 1GB
    }
    reverse_proxy 127.0.0.1:8081
}
```

---

## 📱 Connecting Mobile OPDS Readers

Vailib provides a standard OPDS (Open Publication Distribution System) feed compatible with all mobile reading applications:
- **OPDS Feed URL**: `http://<your-server-ip>:8081/opds/` (or `https://books.example.com/opds/`)
- **Supported Apps**:
  - **iOS**: KyBook 3, MapleRead, Marvin 3, TiReader
  - **Android**: Moon+ Reader Pro, FBReader, Aldiko, PocketBook Reader
  - **E-Ink Tablets**: Onyx NeoReader, KOReader

---

## 🛠️ Maintenance & Useful Commands

### Viewing Logs
```bash
# View application and web logs
docker compose logs -f app

# View database logs
docker compose logs -f db
```

### Triggering Manual Catalog Scan
```bash
# Via filesystem trigger
touch ./books/.trigger_scan

# Or via container CLI
docker exec -it vailib-app python3 /sopds/manage.py sopds_scanner scan
```

### Updating Vailib
```bash
git pull origin main
docker compose up -d --build
```

### Creating Database Backup
```bash
docker exec -t vailib-db pg_dump -U sopds sopds > backup_$(date +%Y%m%d).sql
```

---

## 📁 Repository File Overview

| File / Folder | Description |
| :--- | :--- |
| `docker-compose.yml` | Standard compose file configured with relative volumes and health checks |
| `Dockerfile_vailib` | Multi-stage Docker build packaging Python 3.10, Calibre, DjVuLibre, OCR |
| `install.sh` | Interactive, cross-platform CLI installer |
| `views.py` | Backend controller views (UploadView, ReaderView, PopulateView, SetupWizardView) |
| `urls.py` | URL routing definitions |
| `models.py` | Catalog models and 12-language Unicode script index definitions |
| `middleware.py` | Theme detection and setup wizard routing middlewares |
| `scanner_watcher.sh` | File watcher monitoring `.trigger_scan` triggers |
| `bot.sh` | Telegram document bot daemon with atomic configuration polling |
| `convert.sh` | Calibre and OCR automated conversion daemon |
| `download_popular_books.py` | Project Gutenberg & Standard Ebooks crawler |
| `templates/` | Django templates supporting OLED Dark and E-Ink Zero-JS modes |
| `static/custom/` | Stylesheets (`modern.css`, `admin_theme.css`) and client-side scripts |

---

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome!
Feel free to open an issue or submit a pull request on GitHub:
👉 **[https://github.com/vikgr/vailibos](https://github.com/vikgr/vailibos)**

---

## ⚖️ Credits & License

- **License**: GNU General Public License v3.0 ([GPL-3.0](LICENSE)).
- **Foundation**: Built upon [SOPDS](https://github.com/zveronline/sopds) by **zveronline**.
- **Modernization & Architecture**: Engineered by **vikgr**.
