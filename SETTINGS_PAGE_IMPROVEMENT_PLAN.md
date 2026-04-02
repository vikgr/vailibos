# 🛠️ SOPDS Settings Page — Improvement Plan

> **Scope:** `http://opds.workzilla.nl/admin/constance/config/`  
> **Approach:** Pure CSS + JS injection via `admin_theme.css` and `templates/admin/base.html` — **no backend/Django changes needed**, fully achieved through the existing bind-mount system.  
> **Status:** 📋 PLANNED — not yet implemented

---

## 📸 Current State Audit

The page has **7 sections** and **~35 fields** rendered inside a single massive scrolling form:

| # | Section | Fields | Main Problems |
|---|---------|--------|---------------|
| 1 | General Options | 5 | Textarea for simple paths; language dropdown works but no preview |
| 2 | Server Options | 8 | All checkboxes look identical — no visual differentiation |
| 3 | Scanner Options | 8 | Many rarely-used INPX checkboxes clutter the view |
| 4 | Scanner Schedule | 4 | Raw cron strings — confusing for non-technical users |
| 5 | Telegram Bot Options | 3 | API token shown in plain text |
| 6 | Converters Options | 3 | Paths in large textareas — wasteful |
| 7 | Log & PID Files | 6 | 6 path fields that nobody ever changes — pure noise |

**Key pain points:**
- Page requires 6+ scrolls to reach the Save button
- All 35 fields are equally weighted — critical vs. rarely-changed look the same
- Checkboxes render as tiny native browser elements
- Multi-line textareas used for single-line values (paths, codepages)
- No feedback when something is modified before saving
- Cron syntax fields are opaque (e.g., `SOPDS_SCAN_SHED_DOW = *`)
- Telegram API token is visible in plaintext

---

## 🎯 Improvement Areas

### Area 1 — Layout & Navigation (High Impact, Pure CSS/JS)

#### 1.1 — Collapsible Sections
**Problem:** All 7 sections are always expanded — the page is overwhelming.  
**Solution:** Make each section header a toggle that collapses/expands the section body.  
- Default state: **Section 1 (General)** and **Section 2 (Server)** open; sections 4–7 collapsed
- Use a `▼`/`▶` chevron icon in the header  
- Persist open/closed state in `localStorage` per section
- Smooth CSS `max-height` transition animation

**Implementation:** JS + CSS injected via `admin_theme.css` and a `<script>` block in `base.html`.

#### 1.2 — Sticky "Save" Bar
**Problem:** The Save button is at the very bottom — requires scrolling past all 35 fields.  
**Solution:** Add a **fixed/sticky action bar** at the top of the content area that:
- Shows: **"⚙️ SOPDS Configuration"**
- Has a prominent **"💾 Save Settings"** button
- Shows a subtle **"N field(s) modified"** badge when changes are detected (JS)
- Has a **"↺ Reset All"** link (with confirmation dialog)

**Implementation:** JavaScript appends a sticky `div` after DOM load; CSS positions it.

#### 1.3 — Section Jump Navigation
**Problem:** No way to quickly jump to a section.  
**Solution:** Add a compact **vertical quick-nav** floating on the right side:

```
⚙ General
🖥 Server
🔍 Scanner
⏰ Schedule
🤖 Telegram
⚙ Converters
📄 Logs & PIDs
```

Each item scrolls to the matching section. Active section highlighted on scroll.  
**Implementation:** Pure JS + CSS, injected via `base.html`.

---

### Area 2 — Widget Upgrades (High Impact)

#### 2.1 — Toggle Switches for Booleans
**Problem:** Native `<input type="checkbox">` are tiny and visually flat.  
**Solution:** Replace all checkbox fields with a styled **iOS-style toggle switch** using CSS.  
The actual `<input type="checkbox">` remains for form submission.

Color coding:
- **Green glow** when enabled (`--accent-teal`)
- **Muted** when disabled (`--text-muted`)

All 14 boolean fields get this treatment.

**Implementation:** CSS `input[type=checkbox]` widget override + label styling.

#### 2.2 — Single-Line Inputs for Path/Short Fields
**Problem:** Many fields use `<textarea>` but only ever contain a single short value.  
**Solution:** Override CSS to make these fields appear as compact single-line inputs.

Fields to single-line:
- `SOPDS_ROOT_LIB`, `SOPDS_NOCOVER_PATH`, `SOPDS_ZIPCODEPAGE`
- `SOPDS_FB2TOEPUB`, `SOPDS_FB2TOMOBI`, `SOPDS_TEMP_DIR`
- All 6 Log & PID path fields

**Implementation:** CSS targeting `textarea[name="SOPDS_ROOT_LIB"]` etc. with `height: 38px; resize: none`.

#### 2.3 — File Extension Tag Chips
**Problem:** `SOPDS_BOOK_EXTENSIONS` is a raw space-separated string in a textarea.  
**Solution:** Display values as colored **tag chips** below the input, built dynamically.
- Each chip shows the extension (e.g., 📄 `.pdf`, 📖 `.epub`)
- Chips update live as user types
- Chips are decorative only (textarea still submits)

**Implementation:** JS reads textarea value, renders chip `<span>` elements below it.

#### 2.4 — API Token Masking
**Problem:** `SOPDS_TELEBOT_API_TOKEN` shows the full token in visible text.  
**Solution:** Add a **"👁 Show / 🙈 Hide"** toggle button next to the field.  
- Default: masked
- Click to reveal/hide  

**Implementation:** JS toggle button + CSS class to mask.

#### 2.5 — Cron Schedule Human Summary
**Problem:** `SOPDS_SCAN_SHED_MIN/HOUR/DAY/DOW` are raw cron fields — opaque.  
**Solution:** Add a **human-readable summary** below the four fields:

```
⏰ Runs at 03:00 on day 10 of every month (any weekday)
```

Plus a **preset dropdown**:
- `Every day at 3 AM`
- `Every Sunday at midnight`
- `Weekly (Monday 3 AM)`
- `Once a month (1st, 3 AM)`
- `Custom`

**Implementation:** JS event listeners on the four cron fields + preset dropdown.

---

### Area 3 — UX Enhancements

#### 3.1 — Unsaved Changes Warning
- JS detects any field `input`/`change` event
- Shows sticky bar badge in amber: "⚠️ Unsaved changes"
- Intercepts `beforeunload` with browser confirmation dialog

#### 3.2 — Quick Settings Search / Filter
- Search box at top filters rows by label or `SOPDS_` key name
- Non-matching rows fade/hide; non-matching sections auto-collapse
- `Escape` to clear; `Ctrl+F` hijacked on this page

#### 3.3 — Reset-to-Default Confirmation
- Intercept reset link clicks
- Show inline popover: `Reset SOPDS_XXXX to "<default>"? [Yes] [No]`

#### 3.4 — Modified Field Highlight
- Left accent border (`border-left: 3px solid var(--accent)`) on modified rows
- Small `MODIFIED` badge pill shown inline

---

### Area 4 — Section-Specific Improvements

#### 4.1 — Telegram Section: Bot Status Badge
- Section header shows: `🟢 Connected` / `🔴 Offline` / `⚪ Disabled`
- Fetched via JS `getMe` call to Telegram API using the stored token
- Cached for 30 seconds

#### 4.2 — Language Selector Preview
- When `SOPDS_LANGUAGE` dropdown changes, show:  
  `Preview: "Catálogos | Livros | Autores | Gêneros | Séries"`
- Maps to known `vailibDict` translations

#### 4.3 — Auto-Collapse "Log & PID Files" Section
- Section 7 collapsed by default
- Warning note shown when expanded: _"⚠️ Internal system paths — only change if you know what you're doing."_

---

### Area 5 — Implementation Strategy

#### Phase A — CSS Only (30–45 min, zero-risk)
1. Toggle switch styling for all checkboxes
2. Single-line textarea overrides for path fields
3. Sticky Save button (CSS override on `.submit-row`)
4. Modified row left-border accent
5. Better section header styling

#### Phase B — JS Core (1–2 hours)
6. Collapsible sections + localStorage persistence
7. Modified fields counter + unsaved warning
8. Tag chips for `SOPDS_BOOK_EXTENSIONS`
9. API token masking for `SOPDS_TELEBOT_API_TOKEN`
10. Quick settings search / filter

#### Phase C — Advanced UX (optional, 1–2 hours)
11. Cron human-readable summary + presets
12. Reset confirmation popover
13. Telegram bot status badge
14. Language preview box

---

## 📂 Files to Modify

| File | Change |
|------|--------|
| `vailib/static/custom/css/admin_theme.css` | Phase A CSS additions |
| `vailib/templates/admin/base.html` | Phase B/C JS in `<script>` block gated to constance page |

**Deployment:** `scp` files → `docker restart sopds` — no container rebuild needed.

---

## 📅 Suggested Order

```
Phase A (CSS polish)   →   Phase B (JS core)   →   Phase C (advanced, optional)
  ~45 minutes               ~2 hours                  ~2 hours
```
