# ðŸ¤– AI Context: The Unified Vailib Project (v4.0)

**ATTENTION ASSISTANT**: If you are reading this, continue the development of **Vailib**, a unified digital library system at `https://opds.workzilla.nl`. This merges a custom Telegram Doc Converter Bot with a heavily modified SOPDS (Simple OPDS) catalog.

---

## ðŸ“ Environment Topology
- **Local Machine**: `C:\Users\vik\Documents\devops\vailib\` â€” THIS IS THE CANONICAL SOURCE. Do NOT use `casaos/` folder.
- **Remote Host**: `hproliant` (192.168.31.115). User: `vik`. Sudo Password: `[[PASSWORD_HIDDEN]]`.
- **Container**: `sopds` Docker container.
- **Library mount**: `/library` â€” used by both the Telegram Bot and SOPDS scanner.

---

## ðŸš€ Deployment: How to Push Changes

### Files that ARE bind-mounted (copy to /tmp/sopds_custom):
```powershell
# Copy local files to server home
scp modern.css views.py templates/sopds_main.html templates/sopds_books.html templates/sopds_catalogs.html templates/sopds_hello.html templates/sopds_logo.html templates/sopds_menu.html hproliant:~/
# Move to mount point on server
ssh hproliant "echo [[PASSWORD_HIDDEN]] | sudo -S cp ~/modern.css /tmp/sopds_custom/static/css/modern.css && echo [[PASSWORD_HIDDEN]] | sudo -S cp ~/views.py /tmp/sopds_custom/views.py && echo [[PASSWORD_HIDDEN]] | sudo -S cp ~/sopds_main.html /tmp/sopds_custom/templates/sopds_main.html && echo [[PASSWORD_HIDDEN]] | sudo -S cp ~/sopds_books.html /tmp/sopds_custom/templates/sopds_books.html && echo [[PASSWORD_HIDDEN]] | sudo -S cp ~/sopds_catalogs.html /tmp/sopds_custom/templates/sopds_catalogs.html && echo [[PASSWORD_HIDDEN]] | sudo -S cp ~/sopds_hello.html /tmp/sopds_custom/templates/sopds_hello.html && echo [[PASSWORD_HIDDEN]] | sudo -S cp ~/sopds_logo.html /tmp/sopds_custom/templates/sopds_logo.html && echo [[PASSWORD_HIDDEN]] | sudo -S cp ~/sopds_menu.html /tmp/sopds_custom/templates/sopds_menu.html"
```

### Files NOT bind-mounted (must use `docker cp` directly):
```powershell
# Copy local templates to server
scp templates/sopds_authors.html templates/sopds_series.html templates/sopds_breadcrumbs.html hproliant:~/templates/
# Force copy into running container
ssh hproliant "echo [[PASSWORD_HIDDEN]] | sudo -S docker cp ~/templates/sopds_authors.html sopds:/sopds/sopds_web_backend/templates/sopds_authors.html && echo [[PASSWORD_HIDDEN]] | sudo -S docker cp ~/templates/sopds_series.html sopds:/sopds/sopds_web_backend/templates/sopds_series.html && echo [[PASSWORD_HIDDEN]] | sudo -S docker cp ~/templates/sopds_breadcrumbs.html sopds:/sopds/sopds_web_backend/templates/sopds_breadcrumbs.html"
```

### Always restart after deploying:
```powershell
ssh hproliant "echo [[PASSWORD_HIDDEN]] | sudo -S docker restart sopds"
```

### CRITICAL: Bump CSS version on every `modern.css` change:
Change `?v=XX` in `templates/sopds_main.html` line 16. Currently at `?v=34`.

---

## ðŸŽ¨ Theme System (modern.css)

Two themes controlled via `data-theme` attribute on `<html>`:
- **`data-theme="premium"` (OLED)**: Dark sidebar layout, neon cyan accents, glassmorphism.
- **`data-theme="eink"` (E-Ink)**: White BG, black text, top-bar layout, thick borders.

Toggle via button in sidebar â†’ saves to `localStorage('sopds-theme')`.

### Cover image strategy:
| File | Role |
|------|------|
| `cover0.jpg` | âŒ White engineering hexagon â€” **NEVER use as fallback in OLED** |
| `cover1.jpg` | âœ… Dark gradient triangle â€” **universal OLED fallback** |
| `cover2.jpg` | âœ… White engineering hexagon â€” **E-Ink fallback via CSS `content:` override** |

CSS rule that swaps covers in E-Ink mode:
```css
[data-theme="eink"] img[src^="/static/images/cover"] {
    content: url("/static/images/cover2.jpg");
}
```

---

## ðŸ› Known Bugs & Pending Tasks
1. **Top Bar Button Refinement**: Ensure consistent alignment/sizing as catalog grows.
2. **Extreme E-Ink Verification**: Check on physical hardware (Kindle/Kobo) for any remaining background artifacts.

---

## âœ… Completed Features (Phase 4 â€” March 2026)
- **Blue Glow Elimination**: Fixed root-level radial gradients and pseudo-element leaks in E-Ink.
- **Aggressive Monochromatization**: Pure #FFF/#000 palettes, serif font stack.
- **Touch-Friendly E-Ink**: Removed all `:hover` visual changes to prevent artifacts; preserved `.active` states.
- **Search Simplified**: Removed outer borders and gradients from search wrappers.
- **Unified Breadcrumb Engine**: Clickable navigation with clickable dict support implemented in backend (`views.py`) and templates.
- **Localized Labels**: Fixed unrendered "Directory" label by using existing "Catalogs" (ÐšÐ°Ñ‚Ð°Ð»Ð¾Ð³Ð¸) translation. 
- **Busted Cache Engine**: Implemented `?v=XX` for real-time CSS updates.

---

## ðŸ¤– Part 1: The Converter Bot
Bot handles PDF/DJVU files sent to Telegram.
- **Files**: `bot.sh`, `Dockerfile_converter`
- **Converts**: DJVU â†’ PDF via `djvu2pdf` + Ghostscript; image PDFs via `ocrmypdf`
- **Deposits output to**: `/library` volume
- **Notifications**: Sends Telegram updates on progress

---

## ðŸ”œ Next Session Priorities
1. Fine-tune top-bar button alignment for smaller screens.
2. Mobile theme optimization for catalog cards.
3. Final hardware-level verification.
