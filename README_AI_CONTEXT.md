# 🤖 AI Agent Context & Developer Blueprint: Vailib Ecosystem (v5.0)

> **ATTENTION AI AGENT / ASSISTANT**:  
> You are reading the technical specification and developer blueprint for **Vailib (vailibos)**.  
> Read this entire document before proposing or applying code changes, debugging, or introducing new features.

---

## 1. System Architecture Overview

Vailib is a containerized digital library ecosystem based on Django 2.1.15 and Python 3.10. It unifies web catalog browsing, in-browser eBook reading, OPDS catalog feeds, automated background document conversions, a Telegram assistant bot, and scheduled catalog indexing into a single Debian-based container.

```
┌────────────────────────────────────────────────────────────────────────┐
│                         VAILIB UNIFIED CONTAINER                       │
│                                                                        │
│  ┌──────────────────────┐  ┌────────────────────────────────────────┐  │
│  │   Tornado / Django   │  │           Background Daemons           │  │
│  │     Web & OPDS       │  │                                        │  │
│  │   (:8001 -> :8081)   │  │  • scanner_watcher.sh (.trigger_scan)  │  │
│  └──────────┬───────────┘  │  • bot.sh (Telegram Bot Assistant)     │  │
│             │              │  • convert.sh (Calibre / OCR Worker)   │  │
│             │              └────────────────────────────────────────┘  │
│             ▼                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       PostgreSQL Database                        │  │
│  │        (opds_catalog_book, opds_catalog_author, constance)       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │   Host Book Volume /library │
                     └─────────────────────────────┘
```

---

## 2. Core Python / Django Applications

### `opds_catalog` (Core Catalog Engine)
- **`models.py`**: Defines core library entities (`Book`, `Author`, `Series`, `bauthor`, `bseries`, `Catalog`, `Genre`, `bookshelf`, `Counter`, `lang_menu`).
- **`opdsdb.py`**: Low-level database operations, catalog tree creation, duplicate resolution, and logical deletion management.
- **`sopdscan.py`**: Recursive filesystem scanner (`os.walk`), ZIP archive traversal (`processzip`), and INPX catalog parser.
- **`dl.py`**: Stream download handler with on-the-fly filename transliteration (`getFileName`) and ZIP archive packaging.
- **`middleware.py`**: Custom middlewares (`VailibThemeMiddleware`, `SOPDSSetupMiddleware`).
- **`zipf.py`**: Custom ZIP filesystem adapter with encoding fallbacks for CP866 and CP437.

### `sopds_web_backend` (Web Frontend & Management)
- **`views.py`**: Web request handlers (`UploadView`, `ReaderView`, `PopulateView`, `SetupWizardView`, `LanguagesView`, `SearchBooksView`, etc.).
- **`urls.py`**: URL routing table for web routes under `/web/`.
- **`templates/`**: Dual-identity Jinja2/Django templates (`sopds_main.html`, `sopds_reader.html`, `sopds_populate.html`, `sopds_setup.html`, etc.).
- **`static/custom/`**: Modern stylesheets (`modern.css`), admin CSS (`admin_theme.css`), and JavaScript controllers (`theme_switcher.js`, `djvu.js`).

### `constance` (Dynamic Configuration)
- Database-backed configuration backend (`constance.backends.database.DatabaseBackend`).
- Managed dynamically via `/admin/constance/config/` and queried in code via `from constance import config`.

---

## 3. Database Schema & Models

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Author      │       │     bauthor     │       │      Book       │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄─────┐│ id (PK)         │┌─────►│ id (PK)         │
│ full_name       │      └│ author_id (FK)  ││      │ filename        │
│ lang_code       │       │ book_id (FK)    │┘      │ path            │
└─────────────────┘       └─────────────────┘       │ format          │
                                                    │ filesize        │
┌─────────────────┐       ┌─────────────────┐       │ title           │
│     Series      │       │     bseries     │       │ lang            │
├─────────────────┤       ├─────────────────┤       │ lang_code       │
│ id (PK)         │◄─────┐│ id (PK)         │       │ cat_type        │
│ ser             │      └│ ser_id (FK)     │       │ registerdate    │
│ lang_code       │       │ book_id (FK)    │──────►│ annotation      │
└─────────────────┘       │ ser_no          │       │ catalog_id (FK) │
                          └─────────────────┘       └─────────────────┘
```

- **`Book.cat_type`**:
  - `opdsdb.CAT_NORMAL` (`0`): Normal standalone book file on disk.
  - `opdsdb.CAT_ZIP` (`1`): Book file stored inside a compressed `.zip` archive.
  - `opdsdb.CAT_INPX` (`2`): Book indexed via an `.inpx` archive descriptor.

---

## 4. Custom Middleware Architecture

```
Incoming Request
      │
      ▼
┌──────────────────────────────┐
│    VailibThemeMiddleware     │ ──► Inspects: 1. ?theme= query param
└─────────────┬────────────────┘               2. vailib_theme Cookie
              │                                3. User-Agent regex (e-readers -> eink)
              ▼                                Sets request.vailib_theme
┌──────────────────────────────┐
│     SOPDSSetupMiddleware     │ ──► If fresh install (no superuser / no flag),
└─────────────┬────────────────┘     redirects any request to /web/setup/
              │
              ▼
┌──────────────────────────────┐
│     Django View Handler      │
└──────────────────────────────┘
```

### E-Reader User-Agent Detection Regex
Matched against: `kindle`, `kobo`, `nook`, `pocketbook`, `ereader`, `sonyreader`, `eink`, `e-ink`, `boox`, `tolino`, `bookeen`, `onyx`, `remarkable`, `likebook`, `boyue`, `hanvon`, `dasung`, `inkpalm`, `supernote`, `mobiscribe`, `cybook`, `bokeen`, `inkbook`, `opera mini`.

---

## 5. Background Daemons & Inter-Process Communication (IPC)

All daemons are started in `/start.sh` and run concurrently in the container:

### 1. `scanner_watcher.sh` (Catalog Scan Trigger)
```bash
TRIGGER_FILE="/library/.trigger_scan"
while true; do
    if [ -f "$TRIGGER_FILE" ]; then
        rm -f "$TRIGGER_FILE"
        python3 /sopds/manage.py sopds_scanner scan
    fi
    sleep 5
done
```
- **Trigger mechanism**: Web uploads (`UploadView`) or external tools execute `touch /library/.trigger_scan`.

### 2. `bot.sh` (Telegram Document Bot)
- **Config Polling**: Calls embedded Python snippet `check_bot_config()` querying `constance.config.SOPDS_TELEBOT_API_TOKEN` and `SOPDS_TELEBOT_CHAT_ID`.
- **Document Handling**: Incoming PDF/DjVu files are downloaded to `/library/` and enqueued into `/tmp/convert_queue`.
- **Trigger**: Touches `/library/.trigger_scan` on completion.

### 3. `convert.sh` (OCR & Calibre Pipeline)
- Monitors `/tmp/convert_queue` FIFO queue.
- Executes `ebook-convert` or OCR processing and outputs `.epub` or `.fb2` to `/library/`.

---

## 6. In-Browser Reader Architecture (`sopds_reader.html`)

```
                          Reader Router: /web/read/<book_id>/
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
            ePub.js                    PDF.js                 Native XML
          (BOOK_FORMAT == 'epub')   (BOOK_FORMAT == 'pdf')   (BOOK_FORMAT == 'fb2')
                 │                       │                       │
      Binary ArrayBuffer stream      Canvas render            DOMParser XML
                 │                       │                       │
                 └───────────────────────┼───────────────────────┘
                                         ▼
                             Global Keyboard Dispatch
                              (handleReaderKey Event)
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
            Next Page Actions                         Prev Page Actions
      (ArrowRight, PageDown, Space)             (ArrowLeft, PageUp, Shift+Space)
```

### Critical Implementation Details:
1. **ePub.js Scope Trapping**: Keystrokes inside ePub iframe must be captured via `rendition.hooks.content.register((contents) => contents.document.addEventListener('keydown', handleReaderKey))`.
2. **Form Element Guard**: `handleReaderKey` must exit early if `document.activeElement` is `input`, `textarea`, `select`, or `contentEditable`.
3. **Drawer Isolation**: Key events are suppressed when `#settings-drawer` has the `.active` class.

---

## 7. Upload & Extraction Subsystem (`UploadView`)

Located at `/web/upload/` (controller in `views.py`):
- **Request Size Ceiling**: Configured in Django settings via `DATA_UPLOAD_MAX_MEMORY_SIZE = 1073741824` (1 GB) and `FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400` (25 MB buffer).
- **Supported Extensions**: `.epub`, `.fb2`, `.pdf`, `.mobi`, `.djvu`, `.cbr`, `.cbz`, `.azw`, `.azw3`, `.txt`, `.doc`, `.docx`, `.rtf`, `.chm`, `.zip`.
- **ZIP Unpack & Security**:
  - Uses `zipfile.ZipFile` streaming.
  - **Zip Slip Mitigation**: Verifies `os.path.abspath(target_path).startswith(os.path.abspath(dest_dir))`.
  - Preserves `.fb2.zip` single-book archives without unzipping.
  - Automatically touches `/library/.trigger_scan` upon writing files.

---

## 8. Internationalization & 12-Language Matrix

Supported language codes and mappings in `views.py`:
- `en` (English), `ru` (Russian), `de` (German), `el` (Greek), `es` (Spanish), `fr` (French), `ar` (Arabic), `hi` (Hindi), `pt` (Portuguese), `zh-hans` (Chinese Simplified), `bn` (Bengali), `nl` (Dutch).
- Flag CDN format: `https://flagcdn.com/w20/<flag_code>.png`.

---

## 9. AI Agent Coding Guidelines & Safety Rules

When extending or modifying the Vailib codebase, you must adhere to these rules:

1. **Dual-Theme Integrity**: Every template change must support both `vailib_theme == 'premium'` (Glassmorphism OLED) and `vailib_theme == 'eink'` (High-contrast, zero-JS table layout).
2. **Safe Code Replacement**: When editing Python files, verify syntax using `py_compile` before committing.
3. **No Hardcoded Secrets**: Never commit tokens, passwords, private keys, or `.env` credentials into git.
4. **Preserve Comments & Docstrings**: Maintain existing code comments, translations, and encoding declarations.
5. **Git Synchronization**: Always commit with descriptive messages and push to all configured remotes (`vailibos`, `origin`, `prod`).
