# 📢 Vailib v5.0 (vailibos) — Long-Form Articles & Social Media Releases

Comprehensive, rich articles (~5-minute read) with illustrations, storytelling, and technical breakdowns for **LinkedIn, Habr, VC.ru, Medium, Substack, Reddit, and Telegram**.

---

## 🇷🇺 Статья на русском языке (LinkedIn / Хабр / VC.ru / Telegram-лонгрид)

### Заголовок:
# Как мы создали идеальный цифровой книжный сервер: История разработки Vailib v5.0 в паре с Google Deepmind Antigravity 📚⚡

![Vailib v5.0 Hero Banner](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_showcase.jpg)

### Введение: Почему современным библиотекам нужна революция?
Каждый, кто пробовал организовать домашнюю или серверную коллекцию электронных книг, рано или поздно сталкивался с дилеммой. С одной стороны — монструозные решения, перегруженные интерфейсами из 2000-х годов, которые с трудом открываются на смартфонах и намертво вешают браузер на читалках Kindle или Onyx Boox. С другой стороны — закрытые облачные экосистемы, привязывающие пользователя к проприетарным форматам и подпискам.

Классический протокол OPDS (Open Publication Distribution System) — это прекрасный и надежный фундамент. Но мир изменился: нам больше не хочется просто скачивать файл по ссылке. Мы хотим открывать любую книгу прямо в браузере, читать её на любом экране (от 4K OLED монитора до энергоэффективного E-Ink ридера), загружать сотни книг одним перетаскиванием архива и конвертировать сканы документов через Telegram на лету.

Так родился проект **Vailib v5.0 (vailibos)**. Это не просто обновление — это полная перезагрузка концепции self-hosted цифровой библиотеки, созданная в глубоком инженерном симбиозе с **Google Deepmind Antigravity** (автономным AI-ассистентом нового поколения).

---

### 🎨 1. Dual-Identity UI: Два лица одной библиотеки
Одна из главных инженерных проблем веб-интерфейсов для книг — фундаментальная разница между цветными дисплеями высокой плотности и экранами на электронных чернилах (E-Ink).

![OLED Dark Mode vs E-Ink Mode](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_catalog_dark.png)

В Vailib мы отказались от компромиссов и внедрили архитектуру **Dual-Identity**:
1. **OLED Dark Glassmorphism (для ПК, ноутбуков, iPad и смартфонов)**: Глубокая обсидиановая палитра, эффект матового стекла (glassmorphism), неоновые акценты, поддержка плавных анимаций и адаптивная плиточная сетка.
2. **Pure 1-Bit E-INK Mode (для Kindle, Kobo, PocketBook, Nook, Onyx Boox)**: Радикально упрощенный режим. Никаких анимаций, тяжелых скриптов и полупрозрачностей. Высококонтрастная монохромная верстка, четкие контуры и мгновенная перерисовка страниц без гостинга (ghosting).

![E-Ink Mode Preview](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_eink_catalog.png)

*Интерфейс автоматически распознает класс подключенного устройства по User-Agent и параметрам рендеринга, мгновенно отдавая нужную тему, а также сохраняет ручной переключатель в один клик.*

---

### 📖 2. Универсальная читалка прямо в браузере
Забудьте о необходимости устанавливать сторонние читалки для каждого формата. В Vailib v5.0 встроен всеядный ридер с аппаратным ускорением и поддержкой 4 ключевых форматов:
- **EPUB** — с плавной разбивкой на страницы, сохранением стилей и рендерингом через виртуальный поток.
- **FB2** — мгновенный нативный парсер XML-структуры с главами, сносками и цитатами.
- **PDF** — векторная отрисовка через высокопроизводительное полотно PDF.js.
- **DjVu** — клиентский рендеринг через оптимизированное ядро DjVu.js.

![In-Browser Reader](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_reader_epub.png)

#### Удобство чтения:
- **Управление с клавиатуры**: Листайте страницы привычными клавишами: `Стрелка вправо` (`→`), `Пробел`, `Page Down` — вперед; `Стрелка влево` (`←`), `Shift + Пробел`, `Page Up` — назад.
- **Персонализация типографики**: Тонкая настройка размера шрифта, межстрочного интервала, гарнитур (Serif, Sans, Dyslexic, Monospace) и палитр (Тёмная, Светлая, Сепия, E-Ink).

---

### 📤 3. Drag & Drop загрузка и автоматическая распаковка ZIP
Как обычно выглядит добавление новых книг на сервер? Зайти по SSH, скопировать файлы, распаковать, выставить права доступа и вручную запустить сканер.

В Vailib v5.0 этот процесс сокращен до одного жеста:

![Upload and ZIP Unpacker](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_upload_view.png)

1. Открываете страницу **Populate & Upload** в браузере.
2. Перетаскиваете мышью один файл или целую пачку книг (поддерживаются EPUB, PDF, FB2, MOBI, DJVU, CBR, CBZ, AZW3, TXT, DOCX).
3. **Загружаете ZIP-архивы**: Сервер на лету безопасно распаковывает вложенные структуры каталогов, извлекает все книги с защитой от атак типа Zip Slip и автоматически сохраняет нужные метаданные.
4. **Мгновенный автоскан**: Фоновый файловый демон перехватывает событие загрузки и индексирует новые книги в базу данных PostgreSQL в течение нескольких секунд.
5. Поддерживаются файлы и архивы размером **до 1 ГБ**!

---

### 🤖 4. Умный Telegram-бот с авто-OCR и конвертацией
Одна из самых удобных возможностей Vailib — персональный Telegram-бот:
- Нашли PDF-статью, старый скан книги или файл FB2 в пути? Просто отправьте документ в диалог со своим ботом.
- Бот самостоятельно запустит цепочку обработки: проведет оптическое распознавание текста (**OCR** через Tesseract), сконвертирует документ в чистый **EPUB** с помощью Calibre и аккуратно добавит его в вашу домашнюю библиотеку.

---

### 🔍 5. Поиск, фильтры и интеграции
Полнотекстовый поиск по авторам, сериям, жанрам и языкам (с поддержкой 12 языковых матриц: от латиницы и кириллицы до арабского, греческого, деванагари и китайских иероглифов).

![Search Results & Actions](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_search_results.png)

Каждая книга снабжена удобными карточками: чтение в один клик, прямое скачивание нужного формата или отправка на устройства через OPDS-каталог (KyBook, Moon+ Reader, FBReader, Aldiko).

---

### ⚙️ 6. Развертывание за 60 секунд: Docker и Open Source
Проект полностью упакован в переносимый Docker-контейнер и опубликован под свободной лицензией **GPL-3.0**.

![Settings Dashboard](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_settings.png)

#### Быстрый запуск на любом Linux-сервере или VPS:
```bash
curl -fsSL https://raw.githubusercontent.com/vikgr/vailibos/main/install.sh | bash
```

Скрипт автоматически проверит Docker, настроит порты, создаст постоянные тома для книг и базы данных и запустит 6-шаговый веб-мастер первой настройки.

---

### 💡 Заключение: Опыт парной разработки с AI
Разработка Vailib v5.0 стала наглядным примером того, как передовые автономные системы вроде **Google Deepmind Antigravity** трансформируют процесс создания сложного ПО:
- От глубокого рефакторинга устаревшей кодовой базы до написания чистых CSS/JS модулей.
- От проектирования контейнерной архитектуры до автоматического тестирования и генерации документации для людей и AI-агентов.

🌟 **Исходный код доступен на GitHub**:
- 🚀 Публичный релизный репозиторий: [https://github.com/vikgr/vailibos](https://github.com/vikgr/vailibos)
- 🛠️ Исходный мастер-проект: [https://github.com/vikgr/vailib](https://github.com/vikgr/vailib)

Будем рады вашим звёздам ⭐, фидбеку и Issue на GitHub! Приятного чтения!

---

## 🇬🇧 Long-Form English Article (LinkedIn / Medium / Substack / Reddit r/selfhosted / Dev.to)

### Title:
# Re-Engineering the Self-Hosted Digital Library: Inside Vailib v5.0 — Built with Google Deepmind Antigravity 📚⚡

![Vailib v5.0 Hero Banner](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_showcase.jpg)

### Introduction: The Problem with Modern eBook Servers
For decades, personal digital library software has occupied one of two extremes. On one side are monolithic, legacy OPDS servers with clunky mid-2000s Web 1.0 interfaces that render painfully slow on smartphones and crash e-ink browsers. On the other side are walled-garden cloud platforms that lock your personal library behind recurring subscriptions and proprietary formats.

The OPDS (Open Publication Distribution System) standard is brilliant, but user expectations have evolved. Readers don’t just want an XML feed to download a file; they want:
- Instant in-browser reading across any screen without installing third-party apps.
- Hardware-aware interfaces that look breathtaking on 4K OLED displays yet switch to pure 1-bit monochrome on Kindle and Onyx devices.
- Seamless drag-and-drop book uploads with automatic ZIP extraction.
- Automated OCR and document conversion via Telegram.

To solve this, we engineered **Vailib v5.0 (vailibos)** — a modern, containerized, open-source personal digital library and OPDS powerhouse, co-developed end-to-end with **Google Deepmind's Antigravity** (Advanced Agentic AI Coding Assistant).

---

### 🎨 1. Hardware-Aware Dual-Identity UI Architecture
Most web applications try to force a single responsive layout across every device. But an iPad with a 120Hz Retina screen and a 6-inch E-Ink Kindle have fundamentally conflicting visual and rendering requirements.

![OLED Dark Mode vs E-Ink Mode](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_catalog_dark.png)

Vailib resolves this with a dedicated **Dual-Identity Engine**:
1. **Obsidian OLED Dark Glassmorphism (Desktop / Mobile)**:
   - Deep indigo/violet palette designed for high contrast and battery savings on OLED panels.
   - Frosted glass cards (backdrop-filter glassmorphism), subtle neon gradients, and fluid transitions.
2. **Pure 1-Bit High-Contrast E-INK Mode (Kindle / Kobo / PocketBook / Onyx Boox / Remarkable)**:
   - Eliminates all CSS transitions, animations, and non-essential JS.
   - High-contrast 1-bit typography and solid borders preventing e-ink display ghosting.

![E-Ink Mode Preview](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_eink_catalog.png)

*Hardware auto-detection evaluates User-Agent profiles and screen capabilities on connection, seamlessly serving the optimal theme with zero friction.*

---

### 📖 2. Universal In-Browser Book Reader
Reading on Vailib is completely frictionless. With a single click, any book opens in a dedicated reader supporting four major formats:
- **EPUB**: Rendered via an optimized ePub.js stream with single-column pagination and instant chapter navigation.
- **FB2**: High-speed native XML DOM parser preserving section hierarchies, notes, and epigraphs.
- **PDF**: Canvas rendering powered by PDF.js with responsive zoom and page jumping.
- **DjVu**: Client-side decoding powered by DjVu.js.

![In-Browser Reader](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_reader_epub.png)

#### ⌨️ Full Keyboard Navigation
Navigate large novels effortlessly using standard keyboard shortcuts:
- **Next Page**: `Right Arrow` (`→`), `Page Down` (`PgDn`), `Space`, `Down Arrow` (`↓`)
- **Previous Page**: `Left Arrow` (`←`), `Page Up` (`PgUp`), `Shift + Space`, `Up Arrow` (`↑`)

Readers can customize font sizes (12px–28px), switch typography (Serif, Sans, Dyslexic, Monospace), and toggle reading palettes (OLED Dark, Paper Sepia, Light, E-Ink).

---

### 📤 3. Drag & Drop Upload with Smart Multi-Book ZIP Extraction
Adding books to a self-hosted library should never require manual SSH commands or complex folder mounting.

![Upload and ZIP Unpacker](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_upload_view.png)

Vailib’s **Populate & Upload** suite introduces:
- **Drag-and-Drop Ingestion**: Drop single files or dozens of books at once (`.epub`, `.pdf`, `.fb2`, `.mobi`, `.djvu`, `.cbr`, `.cbz`, `.azw3`, `.txt`, `.docx`).
- **Automated ZIP Extraction**: Uploading a `.zip` archive triggers an intelligent unpacker that extracts all contained books recursively into the library while enforcing strict Zip Slip security boundaries.
- **Instant Background Indexing**: File system events immediately trigger the catalog watcher, updating the PostgreSQL database in under 5 seconds.
- **High-Capacity Pipeline**: Handles large scanned PDF and DjVu volumes up to **1 GB per upload**.

---

### 🤖 4. Autonomous Telegram OCR & Conversion Bot
Vailib includes an integrated Telegram daemon:
- Forward any research paper, book scan, or FB2 file to your private Telegram bot.
- The bot triggers **Tesseract OCR** for image recognition, converts the document to standardized **EPUB** using Calibre, and places the finished book directly into your catalog.

---

### 🔍 5. Rich Search, Categorization, & 12-Language Matrix
Search across titles, authors, and series in milliseconds with instant format tags and one-click action buttons:

![Search Results & Actions](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_search_results.png)

Vailib also features a full **12-Language Global Matrix** with native script detection (Latin, Cyrillic, Greek, Arabic, Devanagari, Bengali, Hanzi).

---

### ⚙️ 6. 60-Second Universal Deployment
Vailib runs as an optimized, multi-stage Docker container backed by PostgreSQL:

![Settings Dashboard](https://raw.githubusercontent.com/vikgr/vailib/main/docs/images/vailib_real_settings.png)

#### Run on any Linux, VPS, Raspberry Pi, or macOS host:
```bash
curl -fsSL https://raw.githubusercontent.com/vikgr/vailibos/main/install.sh | bash
```

The interactive installer verifies Docker prerequisites, maps your storage paths, launches the stack, and guides you through a 6-step web setup wizard.

---

### 🚀 The Power of AI Pair-Programming with Antigravity
Building Vailib v5.0 was an extraordinary demonstration of modern agentic coding with **Google Deepmind Antigravity**:
- Rapid refactoring of core Django/SOPDS internals.
- End-to-end creation of glassmorphic CSS, responsive JavaScript reader modules, and headless browser validation.
- Automated Docker multi-stage builds and dual-audience documentation (for humans and AI developer subagents).

🌟 **Open Source & Available Now on GitHub (GPL-3.0)**:
- 📦 Public Release Repo: [https://github.com/vikgr/vailibos](https://github.com/vikgr/vailibos)
- 🛠️ Master Development Repo: [https://github.com/vikgr/vailib](https://github.com/vikgr/vailib)

Give it a star ⭐ on GitHub, spin it up on your home lab or VPS, and enjoy your books like never before!

---

#OpenSource #SelfHosted #HomeLab #Docker #DigitalLibrary #eBook #EInk #Kindle #Python #Django #Antigravity #GoogleDeepmind #AI
