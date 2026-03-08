# 🤖 AI Context: The Unified Vailib Project (v4.0)

**ATTENTION ASSISTANT**: If you are reading this, continue the development of **Vailib**, a unified digital library system at `https://opds.workzilla.nl`. This merges a custom Telegram Doc Converter Bot with a heavily modified SOPDS (Simple OPDS) catalog.

---

## 📁 Environment Topology
- **Local Machine**: `C:\Users\vik\Documents\devops\vailib\` — THIS IS THE CANONICAL SOURCE. Do NOT use `casaos/` folder.
- **Remote Host**: `hproliant` (192.168.31.115). User: `vik`. Sudo Password: `1j2k3l`.
- **Container**: `sopds` Docker container.
- **Library mount**: `/library` — used by both the Telegram Bot and SOPDS scanner.

---

## 🚀 Deployment: How to Push Changes

### Files that ARE bind-mounted (copy to /tmp/sopds_custom):
```powershell
scp modern.css views.py templates/sopds_main.html templates/sopds_hello.html templates/sopds_logo.html templates/sopds_menu.html hproliant:~/
ssh hproliant "echo 1j2k3l | sudo -S cp ~/modern.css /tmp/sopds_custom/static/css/modern.css && echo 1j2k3l | sudo -S cp ~/views.py /tmp/sopds_custom/views.py && echo 1j2k3l | sudo -S cp ~/sopds_main.html /tmp/sopds_custom/templates/sopds_main.html && echo 1j2k3l | sudo -S cp ~/sopds_hello.html /tmp/sopds_custom/templates/sopds_hello.html && echo 1j2k3l | sudo -S cp ~/sopds_logo.html /tmp/sopds_custom/templates/sopds_logo.html && echo 1j2k3l | sudo -S cp ~/sopds_menu.html /tmp/sopds_custom/templates/sopds_menu.html"
```

### Files NOT bind-mounted (must use `docker cp` directly):
```powershell
scp templates/sopds_authors.html templates/sopds_series.html templates/sopds_books.html templates/sopds_catalogs.html templates/sopds_breadcrumbs.html hproliant:~/templates/
ssh hproliant "echo 1j2k3l | sudo -S docker cp ~/templates/sopds_authors.html sopds:/sopds/sopds_web_backend/templates/sopds_authors.html && echo 1j2k3l | sudo -S docker cp ~/templates/sopds_series.html sopds:/sopds/sopds_web_backend/templates/sopds_series.html && echo 1j2k3l | sudo -S docker cp ~/templates/sopds_books.html sopds:/sopds/sopds_web_backend/templates/sopds_books.html && echo 1j2k3l | sudo -S docker cp ~/templates/sopds_catalogs.html sopds:/sopds/sopds_web_backend/templates/sopds_catalogs.html && echo 1j2k3l | sudo -S docker cp ~/templates/sopds_breadcrumbs.html sopds:/sopds/sopds_web_backend/templates/sopds_breadcrumbs.html"
```

### Always restart after deploying:
```powershell
ssh hproliant "echo 1j2k3l | sudo -S docker restart sopds"
```

### CRITICAL: Bump CSS version on every `modern.css` change:
Change `?v=XX` in `templates/sopds_main.html` line 16. Currently at `?v=20`.

---

## 🎨 Theme System (modern.css)

Two themes controlled via `data-theme` attribute on `<html>`:
- **`data-theme="premium"` (OLED)**: Dark sidebar layout, neon cyan accents, glassmorphism.
- **`data-theme="eink"` (E-Ink)**: White BG, black text, top-bar layout, thick borders.

Toggle via button in sidebar → saves to `localStorage('sopds-theme')`.

### Cover image strategy:
| File | Role |
|------|------|
| `cover0.jpg` | ❌ White engineering hexagon — **NEVER use as fallback in OLED** |
| `cover1.jpg` | ✅ Dark gradient triangle — **universal OLED fallback** |
| `cover2.jpg` | ✅ White engineering hexagon — **E-Ink fallback via CSS `content:` override** |

CSS rule that swaps covers in E-Ink mode:
```css
[data-theme="eink"] img[src^="/static/images/cover"] {
    content: url("/static/images/cover2.jpg");
}
```

---

## 🐛 Known Bugs TO FIX (Priority for Next Session)

### 1. Raw `{% trans "Directory" %}` tag in catalog (HIGH PRIORITY)
**File:** `templates/sopds_catalogs.html` lines 24–25  
The `{% trans "Directory" %}` tag is split across two lines→ renders as literal text.  
**Fix:** Join into one line: `<p ...>{% trans "Directory" %}</p>`

### 2. Colored book covers visible in E-Ink mode (HIGH PRIORITY)
Real book thumbnail URLs (`/opds/catalog/thumb/ID/`) are NOT caught by the CSS cover override.  
**Fix in `modern.css`:**
```css
[data-theme="eink"] img {
    filter: grayscale(1) contrast(1.15) !important;
}
```

### 3. Folder cards grey background in E-Ink (MEDIUM)
Folder cover wrappers have `background: rgba(0,0,0,0.5)` → grey box in E-Ink.  
**Fix in `modern.css`:**
```css
[data-theme="eink"] .cover-wrapper {
    background: #fff !important;
}
[data-theme="eink"] .fi-folder {
    color: #000 !important;
}
```

### 4. E-Ink borders too heavy for older devices (LOW)
Current: `border: 4-6px solid #000`, `box-shadow: 6px 6px 0 #000`.  
**Fix:** Reduce to 2px borders, remove box-shadow on `.book-card`, `.nav-btn`.

---

## ✅ Completed Features (Phase 4 — March 2026)
- All pages redesigned with thumbnail card grids (books, authors, series, catalog)
- All breadcrumbs are clickable dicts `{'name': ..., 'url': ...}` with full back-navigation
- `sopds_breadcrumbs.html` supports both dict and string breadcrumbs
- Author/Series/Book fallback covers all use `cover1.jpg` (dark triangle) in OLED
- E-Ink cover override via `content: url(cover2.jpg)` for static images
- Theme toggle persists via localStorage
- Django template cache busted via `?v=XX` parameter on CSS link

---

## 🤖 Part 1: The Converter Bot
Bot handles PDF/DJVU files sent to Telegram.
- **Files**: `bot.sh`, `Dockerfile_converter`
- **Converts**: DJVU → PDF via `djvu2pdf` + Ghostscript; image PDFs via `ocrmypdf`
- **Deposits output to**: `/library` volume
- **Notifications**: Sends Telegram updates on progress

---

## 🔜 Next Session Priorities
1. Fix E-Ink bugs listed above (see Bug section)
2. After fixing, bump CSS to `?v=21`
3. Test by toggling E-Ink mode on catalog, author search, and a book-list page
