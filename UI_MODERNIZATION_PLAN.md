# Vailib Modernization Roadmap: Native FastAPI, Multi-Theme & E-Ink SSR Stack

This plan outlines the finalized architectural modernization of the **Vailib Library Ecosystem**. The goal is to build a high-performance, developer-friendly codebase optimized for rapid AI-assisted feature development ("vibecoding"), while fully addressing both extremes of your client base:
1. **Obsolete/Legacy Devices (E-Ink Theme)**: Extremely lightweight, zero-JS, raw semantic HTML that renders instantly on old Kindles, Nooks, and vintage browsers (e.g., Opera Mini).
2. **Modern Devices (Premium Multi-Themes)**: A stunning, high-fidelity visual experience featuring selectable Cyberpunk (neon), Classic (professional slate), and Web 3.0 (glassmorphic gradients) aesthetics.

---

## 🛠️ The Architecture: FastAPI Server-Side Rendering (SSR)

To guarantee that old e-readers (which lack modern ES6+ JavaScript execution or flexbox capabilities) can browse and download books, we will use a **Server-Side Rendered (SSR)** model with **FastAPI + Jinja2 Templates** and **Cookie-based Session Authentication**.

```
                         ┌───────────────────────────────────────┐
                         │          Nginx Proxy Manager          │
                         └───────────────────┬───────────────────┘
                                             │ HTTPS
                         ┌───────────────────▼───────────────────┐
                         │     FastAPI SSR Engine (Jinja2)       │
                         └───────────────────┬───────────────────┘
                                             │
      ┌──────────────────────────────────────┴──────────────────────────────────────┐
      │                                                                             │
┌─────▼─────────────────────────────────────┐ ┌─────────────────────────────────────▼─────┐
│       Premium Multi-Themes                │ │         Stark E-Ink Theme                 │
├───────────────────────────────────────────┤ ├───────────────────────────────────────────┤
│ • Cyberpunk (Neon pink/cyan/yellow glows) │ │ • Zero-JS Semantic HTML                   │
│ • Classic (Clean dark/light professional) │ │ • Linear, static, single-column design    │
│ • Web 3.0 (Frosted glass & gradients)     │ │ • Fast rendering, 0% ghosting footprint   │
└─────┬─────────────────────────────────────┘ └─────┬─────────────────────────────────────┘
      │                                             │
      └──────────────────────────────────────┬──────┘
                                             │
      ┌──────────────────────────────────────┴──────────────────────────────────────┐
      │                                                                             │
┌─────▼─────────────────────────────────────┐ ┌─────────────────────────────────────▼─────┐
│      Async Python Telegram Bot            │ │          PostgreSQL Database              │
│    (python-telegram-bot / aiogram)        │ │         (sopds-db compatibility)          │
└───────────────────────────────────────────┘ └───────────────────────────────────────────┘
```

---

## 🎨 Multi-Theme Design System

We will implement a stateless cookie-based theme switcher (`theme=cyberpunk|classic|web3|eink`). This allows users to select their favorite layout, which is saved in their browser sessions and processed server-side to inject the precise styling sheet.

### 1. Cyberpunk Theme (Modern Neon Retro-Futurism)
* **Background**: Ultra-dark carbon black (`#0a0a0f`) and slate-carbon (`#12121e`).
* **Accents**: Neon Cyan (`#00f0ff`) for primary glows/borders, Hot Pink (`#ff007f`) for interactive buttons/hover states, and Cyber Yellow (`#fffb00`) for warnings/stats.
* **Aesthetics**: Scanline filter overlays, terminal grids, glowing neon drop-shadows, and futuristic display fonts (Orbitron / Rajdhani).

### 2. Classic Theme (Sleek Professional Slate)
* **Background**: Clean dark slate (`#0f172a` / `#1e293b`) or crisp light gray (`#f8fafc`).
* **Accents**: Indigo blue (`#6366f1` / `#4f46e5`) for selectors, and muted gray borders.
* **Aesthetics**: Standard, clean, highly professional card grids, soft borders, and minimalist typography (Inter / System Sans).

### 3. Web 3.0 Theme (Dynamic Cosmic Glassmorphic)
* **Background**: Deep cosmic amethyst (`#090514`) with dark purple glass overlays.
* **Accents**: Vibrant violet-to-cyan gradients (`linear-gradient(135deg, #a855f7, #06b6d4)`), and glowing gradient borders.
* **Aesthetics**: Frosted glass panels (`backdrop-filter: blur(12px)`), glowing holographic card shadows, and modern geometric fonts (Outfit / Outfit Sans).

### 4. E-Ink Theme (Super Simple, Lightweight, Compact)
* **Background & Text**: Strict high-contrast monochrome (`#ffffff` background, `#000000` text).
* **Obsolete Device Constraints**:
  * **Super Compact & Simple**: Designed specifically for low-resolution, small e-ink screens. Layout is linear, compact, and optimized for fast screen refreshing.
  * **Zero JavaScript**: Browsing, searching, page turning, and catalog navigation run entirely on standard semantic HTML elements (links and native POST forms).
  * **Layout Stability**: Completely suppresses hover states, active transitions, transforms, floating headers, and flexbox/grid layout constraints to eliminate Nook/Kindle rendering artifacts and ghosting.

---

## ⚙️ Core Technical Components

### 1. Backend API & Page Renderer (`vailib`)
* **Framework**: FastAPI (Python 3.11+).
* **ORM Engine**: SQLAlchemy 2.0 mapping directly to the existing Postgres database tables (`opds_catalog_book`, `opds_catalog_catalog`, etc.) to **fully preserve existing user/book data**.
* **Authentication**: Secure, server-side HTTP-only Cookies with Session storage. Supported natively by all obsolete browsers without JavaScript token injection.
* **OPDS Endpoint**: Standard XML catalog generation (`/opds/`) for e-reader application synchronization.
* **Web Reader**: Modular server-rendered book page with format-appropriate readers (PDF, EPUB, FB2) embedded cleanly.

### 2. Unified Watcher & Converter Pipeline
* **Scan Daemon**: Runs inside the same container environment, continuously watching the `/library` directory.
* **calibre Integration**: Queues DjVu and PDF conversions to FB2 dynamically using calibre binaries. Reads metadata via `ebook-meta` and updates the PostgreSQL tables in real-time.

### 3. Asynchronous Telegram Bot
* **Framework**: `python-telegram-bot` (asyncio).
* **Shared Database Access**: Connects to the same database session, enabling direct queries for search, authors, system health, and downloads.

---

## 📋 Proposed Implementation Directory Structure

```
/vailib_modern/
├── app/
│   ├── database.py         # SQLAlchemy configuration & engine
│   ├── models.py           # Existing Postgres-compatible models
│   ├── main.py             # FastAPI App initialization & routing
│   ├── config.py           # Settings and environment variables
│   ├── routes/
│   │   ├── web.py          # Theme page controllers (Jinja2 SSR)
│   │   ├── api.py          # JSON API endpoints
│   │   └── opds.py         # OPDS XML feed generation
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── base.html       # Dynamic base shell (selects CSS based on theme cookie)
│   │   ├── cyberpunk/      # Cyberpunk UI templates
│   │   ├── classic/        # Classic UI templates
│   │   ├── web3/           # Web 3.0 UI templates
│   │   ├── eink/           # Lightweight zero-JS E-Ink templates
│   │   └── opds/           # XML templates
│   └── static/
│       ├── cyberpunk.css   # Retro-futuristic cyberpunk rules
│       ├── classic.css     # Clean professional slate rules
│       ├── web3.css        # Cosmic glassmorphic rules
│       └── eink.css        # Minimalist monochrome rules
├── bot/
│   ├── bot.py              # Async Python Telegram Bot
│   └── converter.py        # calibre watcher & converter script
├── Dockerfile              # Unified build file
└── docker-compose.yml      # Multi-service configuration
```

---

## 🤝 Verification & Delivery Plan

### Phase 1: Local Docker Setup & DB Mapping
* Deploy a local Docker Compose test stack mapping all tables successfully.
* Verify SQLAlchemy can write/read records to `opds_catalog_book` perfectly without violating foreign key constraints.

### Phase 2: Multi-CSS & Template Design
* Construct the HTML layouts.
* Audit the **E-Ink** theme in an absolute zero-JS sandbox (disabling JS completely in Chrome DevTools) to ensure 100% browsing capability on legacy devices.
* Polish the **Cyberpunk**, **Classic**, and **Web 3.0** themes.

### Phase 3: Bot & Converter Migration
* Port the old `bot.sh` script to clean async Python.
* Confirm file delivery (`sendDocument`) works reliably.
