# 🤖 AI Context: The Unified Vailib Project (v3.5)

**ATTENTION ASSISTANT**: If you are reading this, your mission is to continue the development of **Vailib**, a unified digital library system. This project merges a custom Telegram Document Converter Bot with a highly modified instance of the SOPDS (Simple OPDS) catalog.

## 📁 Environment Topology
- **Local Machine Paths**: `C:\Users\vik\Documents\devops\vailib\` contains the source files.
- **Remote Host**: `hproliant` (192.168.31.115). User: `vik`. Sudo Password: `1j2k3l`.
- **Target Container Mount Point**: `/library`. This path is absolutely critical. Both the Telegram Bot's output directory and the SOPDS scanner's input directory must target `/library`. Do NOT use `/books` or relative paths.

## 🧠 Part 1: The Converter Bot
The Telegram Bot (housed in `bot.sh`, `bot.py`, `Dockerfile_converter`) accepts PDFs and DJVU files.
- **Conversion Flow**: It utilizes `ocrmypdf` (for image-only PDFs) and `djvu2pdf` & `Ghostscript` (for `.djvu` extensions) to generate clean PDFs.
- **Notification**: Updates the user on Telegram with the conversion progress.
- **Storage**: Deposits the final `.pdf` inside the `/library` volume mount.

## 🎨 Part 2: The UI Redesign Overlay (v3.5)
The legacy SOPDS Django UI has been ruthlessly completely replaced without altering the base Docker image. We inject a custom CSS/HTML architecture live via Docker volume bind-mounts. Check `sopds-docker-compose.yml`.

- **Bound Overrides**:
  - `/tmp/sopds_custom/templates/sopds_main.html` → `/sopds/sopds_web_backend/templates/sopds_main.html` (The overarching dual-identity Flexbox shell).
  - `/tmp/sopds_custom/templates/sopds_menu.html` → Navigation and the Theme Toggle logic.
  - `/tmp/sopds_custom/templates/sopds_logo.html` → The modern Top-Center Search Bar.
  - `/tmp/sopds_custom/templates/sopds_hello.html` → The dynamic Homepage Dashboard Grid.
  - `/tmp/sopds_custom/views.py` → The Django backend (Specifically tweaked to inject `recent_books` into the `hello` template).
  - `/tmp/sopds_custom/static` → Serves `modern.css` and `theme_switcher.js`.

### The Dual Interface Paradigms (`modern.css`)
- **Premium (OLED) `data-theme="premium"`**: A 280px left sidebar, deep dark colors (`#14142D`), glassmorphism (`backdrop-filter`), glowing neon accents.
- **E-Ink `data-theme="eink"`**: A stark, top-to-bottom brutalist block layout, thick massive borders without border-radius or gradients, absolute black on surgical white. The sidebar snaps to the top using media queries & flex-direction changes.

## 🛠️ The Core Issue Remediation
- **Django Translation Tags**: The original code used `{% trans %}` heavily inside URLs, causing massive `NoReverseMatch` failures on the live server. These were fixed by hardcoding essential Russian translations (`Найти`, `Название`, etc.) directly into the bound HTML templates.
- **CSS Caching**: Browsers cache `modern.css` aggressively. Whenever you alter `modern.css`, you MUST bump the `?v=` parameter (e.g. `?v=18` to `?v=19`) inside `sopds_main.html` or the user will not see the layout changes.

## 🔜 Current Mission Objectives (Phase 4)
When resuming work, these are the priority tasks:
1. **Launch `docker-compose.unified.yml`**: Test that the combined deployment cleanly spins up both the Bot Container and the SOPDS Container, with both writing/reading the `/library` volume securely.
2. **Scanner Crontab / Hook**: SOPDS requires the command `python /sopds/manage.py sopds_scanner` to detect new books. The Telegram Bot drops new PDFs into the directory, but they must be parsed. We need an automated way (a hook in the bot, or a fast cron inside SOPDS) to run the scanner.
3. **Stress Testing**: Ensure large .djvu files do not crash the bot container via OOM (Out of Memory) conditions. Adjust container limit blocks if needed.
