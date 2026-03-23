# Vailib Full UI Modernization Plan

🚨 **NEW STRATEGIC PILLAR (RECORDED)** 🚨
**We are completely separating the two UI themes to ensure compatibility and performance:**
1. **E-Ink/Legacy Theme (`eink`)**: Must be EXTREMELY simple, minimalistic, and lightweight to support very old devices (e.g., Opera Mini on Android 2, old Nook Touches). It will use basic, native HTML/CSS without modern grid/flexbox or heavy Javascript. This is a complete departure from using a single layout engine.
2. **Modern Premium Theme (`premium`)**: Will be a separate full-stack implementation using the newest code, modern flexbox/grid, and advanced UI visual effects.

This plan outlines the steps to replace the remaining legacy, table-based user interfaces with the new OLED glassmorphic theme, and simplifying the legacy theme.

## UI Audit Findings
From inspecting the site and the latest screenshot provided, the following areas still run on the old Foundation/Table design and need an upgrade:
1. **Detailed Entity Lists (`sopds_authors.html`, `sopds_books.html`, `sopds_series.html`)**: The lists (e.g., viewing books by an author or books in a series) use old `<table>` layouts with dark/orange alternating row stripes. They are clunky and don't match the new catalog cards.
2. **Pagination Components**: The bottom pagination still relies on generic Foundation CSS styles. It needs to match the dark theme (accent borders, dark backgrounds, glowing active states).
3. **Breadcrumbs (`sopds_breadcrumbs.html`)**: The top navigation paths (e.g., "КНИГИ / ВЫБОР / ПОКАЗАТЬ ВСЕ") are too small and retain legacy formatting.
4. **Login/Forms (`sopds_login.html`)**: The authentication page hasn't been themed and likely looks out of place. 

*(Note: As requested, the E-Ink theme variations will remain completely untouched during this phase to prevent regressions).*

## Proposed Changes

We will execute these changes directly in the `C:\Users\vik\Documents\devops\vailib` project directory. All changes will be synchronized to the `sopds` docker container for live previewing.

### 1. Refactor List Templates
#### [MODIFY] `templates/sopds_authors.html`
- Delete the legacy `<table>`.
- Implement a flexbox-based `<div class="catalog-list">` (similar to what we did for `sopds_catalogs.html`) so authors appear as structured, hoverable rows.

#### [MODIFY] `templates/sopds_books.html`
- Delete the legacy `<table>`.
- Implement a rich list variant showing the book cover thumbnail, title, author, and formats (PDF/FB2/etc.) using the modern CSS classes.

#### [MODIFY] `templates/sopds_series.html`
- Delete the legacy `<table>` and align with the `catalog-list` UI.

### 2. Refactor Navigation & Auth
#### [MODIFY] `templates/sopds_breadcrumbs.html`
- Update the structure to use a modern UI flex row, improving font weight and accenting the separators.

#### [MODIFY] `templates/sopds_login.html`
- Wrap the login form in a `.book-card` or modern auth container with glowing accents and dark inputs.

### 3. Update Stylesheets
#### [MODIFY] `modern.css`
- Add beautiful OLED styling for `.pagination` links (removing default foundation backgrounds).
- Add styling for the new `.list-item` or enhanced book blocks used in the above templates.

## Verification Plan
1. **Local Application**: Write all changes directly into `vailib/templates/` and `vailib/modern.css`.
2. **Live Sync**: Copy the templates into the `library-web` (sopds) docker container template directory and force reload.
3. **Visual Validation**: Launch the browser subagent to fetch screenshots of the `/web/author/?lang=0` page to prove the old striped tables are gone and the UI feels premium.
