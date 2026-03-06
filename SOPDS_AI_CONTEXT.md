# AI Context: SOPDS (Simple OPDS Catalog) & Unified Vailib

## 🌐 Overview
SOPDS is the web and OPDS interface for the library. It is currently being modernized into a dual-theme interface (Premium OLED and High-Contrast E-Ink). It is destined to be merged with a Telegram Converter Bot into a unified container called `Vailib`.

---

## ⚙️ Configuration (Current State)
- **Host**: `hproliant` (192.168.31.115). User: `vik`. Password: `1j2k3l` for sudo.
- **Image**: `zveronline/sopds:latest` (Django-based)
- **Database**: Postgres 13 (Container: `sopds-db`)
- **Library Path**: `/library`

---

## 🎨 UI Redesign Modifications (Live via Volumes)
**MASSIVE ARCHITECTURE CHANGE (V3)**: The original Foundation `.row` and `.column` grid from `sopds_main.html` has been completely annihilated. We have injected a completely custom Flexbox Layout mimicking modern AI and E-reader UI.
1. **`sopds_main.html`**: Rewritten from scratch. It now wraps everything in `.app-wrapper`. It creates a distinct `.sidebar-container` (for navigation) and `.main-content` (for books).
2. **`sopds_menu.html`**: Completely rewritten. Replaced orange dropdowns with solid `.vailib-nav-menu` items. The **Theme Toggle Button** was uniquely placed at the bottom of the sidebar.
3. **`sopds_logo.html`**: Stripped of the cat logo. It now uniquely serves as the "Comfort Search Box", moved directly into the sidebar under the menu.
4. **`modern.css`**: Completely wipes out the legacy `sopds.css` (using `display:none` on `.top-bar` and other original elements).
    * `[data-theme="premium"]` renders a sleek dark UI with a fixed 280px left sidebar and glows.
    * `[data-theme="eink"]` overwrites the Flexbox layout to be `flex-direction: column;`, moving the sidebar to the top, removing borders, and using pure black/white blocks for Kindle-like navigation.
5. **Translations**: To prevent `NoReverseMatch` errors from the Django `{% trans %}` tags malfunctioning, all UI text (Найти, Название, Авторы, Каталог) was explicitly hardcoded into Russian.

*⚠️ AI TROUBLESHOOTING NOTE:*
*If `modern.css` isn't updating, bump the `?v=` number in `sopds_main.html` and restart the container mapping.*

---

## 🚀 Unified `Vailib` Roadmap (Phases 3 & 4)
- **Current Focus**: Web UI polishing.
- Both the SOPDS instance and the local Telegram PDF/Djvu converter bot have been modified to use `/library` uniformly.
- A `docker-compose.unified.yml` has been prepared in the `devops/casaos` folder to launch both systems cohesively.
