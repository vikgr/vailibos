# Plan: Expanded Language Support (Top 10 + Greek)

## Objective
Extend SOPDS book catalog indexing to natively support the 10 most popular global languages plus Greek. Currently, the catalog alphabet filter (`lang_menu` in `models.py`) only supports Cyrillic, Latin, and Digits. We will modify the core codebase to correctly bucket titles in these languages into their respective alphabet groups.

## Current Architecture
In the `zveronline/sopds:latest` container `/sopds/opds_catalog/models.py`, the language grouping is determined by `LangCodes` and `lang_menu`:
- `1`: Cyrillic
- `2`: Latin (covers English, Spanish, French, Portuguese, German)
- `3`: Digits
- `9`: Other symbols
- `0`: Show all

## Top 10 Popular Languages & Scripts
1. **English** - Latin (Already supported)
2. **Mandarin Chinese** - Han Characters (CJK)
3. **Hindi** - Devanagari Script
4. **Spanish** - Latin (Already supported)
5. **French** - Latin (Already supported)
6. **Arabic** - Arabic Script
7. **Bengali** - Bengali Script
8. **Russian** - Cyrillic (Already supported)
9. **Portuguese** - Latin (Already supported)
10. **Urdu** - Perso-Arabic Script (Shares with Arabic)
+ **Greek** - Greek Alphabet

## Implementation Steps

### 1. Update `models.py` (Alphabet Definitions)
We will introduce new language codes and populate their respective character sets in `LangCodes`.

```python
LangCodes = {
    1: 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщьыъэюя', # Cyrillic (Russian)
    2: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', # Latin (EN, ES, FR, PT)
    3: '0123456789', # Digits
    4: 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψωάέήίόύώϊϋ', # Greek
    5: 'ابتثجحخدذرزسشصضطظعغفقكلمنهويپچژگ', # Arabic + Urdu
    6: 'अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह', # Devanagari (Hindi)
    7: 'অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহ', # Bengali
}
```
*Note: Chinese (CJK) characters span thousands of glyphs. Instead of adding a massive string to `LangCodes`, the `dl.py` metadata scanner must be updated to route Unicode blocks for CJK into a dedicated `lang_code=8` bucket.*

### 2. Update `lang_menu` (UI Labels)
Add the lazy-translated labels to the global `lang_menu` dictionary:
```python
lang_menu = {
    1: _lazy('Cyrillic'), 
    2: _lazy('Latin'), 
    3: _lazy('Digits'), 
    4: _lazy('Greek'),
    5: _lazy('Arabic / Urdu'),
    6: _lazy('Devanagari (Hindi)'),
    7: _lazy('Bengali'),
    8: _lazy('Chinese (CJK)'),
    9: _lazy('Other symbols'), 
    0: _lazy('Show all')
}
```

### 3. Update the Book Importer `dl.py`
The importer script inside `/sopds/opds_catalog/dl.py` determines `lang_code` by taking the first character of the `search_title` and checking which `LangCodes` list contains it.
- **Modification**: We will bind-mount a custom `dl.py` via Docker (similar to `/tmp/sopds_custom/dl.py`).
- **Logic change**: If a character falls within the Unicode blocks for CJK (e.g., `\u4e00-\u9fff`), the importer should automatically assign it `lang_code = 8`. For others, it relies on the newly expanded `LangCodes`.

### 4. Deploy and Rescan
- Push the custom `models.py` and `dl.py` to the Docker volume `/tmp/sopds_custom/`.
- Update `docker-compose.unified.yml` / `sopds-docker-compose.yml` to bind-mount `models.py` into `/sopds/opds_catalog/models.py`.
- Restart the container to reload the Python backend configuration.
- Run a full library rescan `docker exec sopds python3 manage.py sopds_scanner clear` to re-bucket existing titles based on the new character maps.

## Deliverables
- [x] Customized `models.py` — expanded `LangCodes` (codes 4–8) live in production.
- [x] Customized `opdsdb.py` — CJK auto-detection via Unicode block ranges (`\u4e00-\u9fff`).
- [x] `sopds-docker-compose.yml` — bind-mounts `models.py` and `opdsdb.py` from `/home/vik/vailib/`.

> **Status**: ✅ Fully deployed as of March 2026 (Phase 3). Run `docker exec sopds python3 manage.py sopds_scanner clear` after any `LangCodes` change to re-bucket existing titles.
