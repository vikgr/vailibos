# 📢 Vailib v5.0 (vailibos) — Long-Form Articles & Social Media Releases

> **Reading Time**: 6–7 minutes (~1,500 words)  
> **Target Platforms**: LinkedIn Articles, Habr (Хабр), VC.ru, VKontakte (Статьи), Medium, Substack, Reddit (`r/selfhosted`, `r/homelab`, `r/programming`), Dev.to.  
> **Repository Link**: [https://github.com/vikgr/vailibos](https://github.com/vikgr/vailibos) *(100% Free & Open Source, GPL-3.0)*

---

## 📊 Исследование: Оптимальная длина статей для соцсетей

| Платформа | Рекомендуемый объём | Время чтения | Формат & Особенности |
| :--- | :--- | :--- | :--- |
| **LinkedIn Articles** | 1,200 – 1,800 слов | 5–7 минут | Сильный лид-абзац, визуальные паузы каждые 200–300 слов, списки буллетов, фокус на инновациях и технологиях. |
| **Хабр (Habr.com)** | 1,500 – 2,500 слов | 7–10 минут | Высокая техническая глубина, схемы архитектуры, реальные скриншоты интерфейса, примеры команд терминала и решения проблем. |
| **VK.com (Статьи)** | 1,000 – 1,600 слов | 5–6 минут | Вёрстка в редакторе статей VK, крупные скриншоты, динамичный живой язык, эмодзи-акценты. |
| **Medium / Substack** | 1,400 – 2,000 слов | 6–8 минут | Сторителлинг, инженерный контекст («почему мы это сделали»), чистая типографика. |
| **Reddit (`r/selfhosted`)** | 800 – 1,400 слов | 4–6 минут | Без лишней воды: фичи, стек, скриншоты, Docker Compose, открытый исходный код и ссылка на GitHub. |

---

## 🇷🇺 Полная статья на русском языке (Хабр / VC.ru / LinkedIn / VK Статьи / Telegram)

### Заголовок:
# Как мы создали идеальный цифровой книжный сервер: История разработки Vailib v5.0 в паре с Google Deepmind Antigravity 📚⚡

![Vailib v5.0 Hero Banner](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_showcase.jpg)

### Введение: Почему домашним библиотекам нужна революция?
Каждый, кто пробовал собрать собственную коллекцию книг и развернуть домашний сервер (self-hosted library), сталкивался с парадоксом. 

С одной стороны — проверенные временем серверы OPDS и каталогизаторы, чей интерфейс застрял в середине 2000-х. Они перегружены таблицами, с трудом открываются со смартфона и намертво вешают встроенные браузеры электронных книг (Kindle, Kobo, Onyx Boox). С другой стороны — закрытые облачные сервисы, где ваши книги привязаны к подписке и проприетарным приложениям.

Мы задали себе вопрос: **какой должна быть идеальная домашняя библиотека в 2026 году?**
- Она должна мгновенно открывать любую книгу (EPUB, FB2, PDF, DjVu) **прямо в браузере**, без сторонних приложений.
- Интерфейс обязан быть **адаптивным к железу**: на мониторах и смартфонах радовать глубоким темным OLED-дизайном, а на читалках с электронными чернилами переключаться в сверхчеткий монохромный режим.
- Добавление книг не должно требовать работы в терминале: перетащил архив `.zip` с десятками книг — сервер сам всё распаковал, рассортировал и добавил на полку.
- А если вы в дороге и нашли скан редкой статьи — просто отправляете PDF или DjVu в Telegram, а умный бот на сервере распознает текст через OCR и соберет аккуратный EPUB.

Так появился **Vailib v5.0 (vailibos)** — полнофункциональный open-source экосистемный проект, созданный в тесном инженерном тандеме с **Google Deepmind Antigravity** (автономным AI-ассистентом нового поколения).

---

### 🎨 1. Dual-Identity UI: Радикальное разделение OLED и E-Ink
Попытка сделать один универсальный дизайн для цветного смартфона и черно-белой читалки всегда приводит к провалу. Анимации и тени, которые великолепно смотрятся на iPad, превращают экран читалки в размытое мерцающее месиво (ghosting).

![OLED Dark Mode Catalog](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_catalog_dark.png)

В Vailib v5.0 реализована концепция **Dual-Identity**:

1. **OLED Dark Obsidian (Desktop, Ноутбуки, Смартфоны)**:
   - Глубокий черный фон для экономии батареи на OLED/AMOLED матрицах.
   - Эффект матового стекла (*glassmorphism*), неоновые акценты и плавная анимация карточек.
   - Информативные виджеты со статистикой (число книг, авторов, жанров и серий) и каруселью новинок.
2. **Pure 1-Bit E-INK Mode (Kindle, Kobo, PocketBook, Onyx Boox, Remarkable)**:
   - Полное отключение CSS-переходов, размытий и тяжелого JavaScript.
   - 100% контрастный монохромный рендеринг, четкие границы кнопок и шрифты высокой резкости.
   - Страницы обновляются мгновенно без артефактов электронных чернил.

![E-Ink Mode Preview](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_eink_catalog.png)

> **Аппаратное авто-определение:** Сервер на лету анализирует User-Agent и параметры дисплея. Если вы заходите с читалки Kindle или Onyx — вы сразу попадаете в оптимизированный E-Ink интерфейс. Для пользователей также доступен переключатель тем в один клик.

---

### 📖 2. Универсальная читалка прямо в браузере с управлением с клавиатуры
Вам больше не нужно скачивать файл на устройство и искать подходящее приложение. Читайте прямо в браузере на любом устройстве:

![In-Browser Book Reader](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_reader_epub.png)

- **EPUB**: Полноценный поток на базе ePub.js с разбивкой на страницы, сохранением стилей и моментальным переходом по главам.
- **FB2**: Высокоскоростной нативный парсер XML-структуры с поддержкой сносок, эпиграфов и форматирования стихов.
- **PDF**: Четкий векторный рендеринг через движок PDF.js.
- **DjVu**: Встроенный клиентский декодер DjVu.js.

#### ⌨️ Управление чтением с клавиатуры:
- **Следующая страница**: `Стрелка вправо` (`→`), `Пробел`, `Page Down` (`PgDn`), `Стрелка вниз` (`↓`)
- **Предыдущая страница**: `Стрелка влево` (`←`), `Page Up` (`PgUp`), `Shift + Пробел`, `Стрелка вверх` (`↑`)

В боковом меню ридера можно на лету менять размер шрифта (от 12px до 28px), выбирать гарнитуры (*Serif, Sans-Serif, OpenDyslexic, Monospace*) и переключать палитры чтения (*OLED Тёмная, Сепия, Бумага, E-Ink*).

---

### 📤 3. Drag-and-Drop загрузка и автоматическая распаковка ZIP-архивов
Раньше для пополнения библиотеки требовалось подключение по SSH, ручное копирование в директории и вызов консольных команд сканера.

В Vailib v5.0 загрузка превратилась в удовольствие:

![Drag & Drop Upload & ZIP Extractor](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_upload_view.png)

1. Откройте раздел **Populate & Upload** (`/web/populate/`).
2. Перетащите в окно браузера один файл или пачку книг любого формата (`.epub`, `.pdf`, `.fb2`, `.mobi`, `.djvu`, `.cbr`, `.cbz`, `.azw3`, `.txt`, `.docx`).
3. **Загрузка архивов `.zip`**: Если вы загружаете ZIP-архив с десятками книг, встроенный распаковщик безопасно извлечет все книги (с защитой от уязвимостей *Zip Slip*) и сохранит их в каталог.
4. **Мгновенный автоскан**: Сервер автоматически зарегистрирует событие появления новых файлов и за 5 секунд добавит их в базу данных.
5. Максимальный размер загрузки расширен **до 1 ГБ** на операцию.

---

### 🔍 4. Поиск, категоризация и 12 языковых матриц
Быстрый поиск по названию, автору, серии или жанру выдает интерактивные карточки с обложками, метаданными и кнопками мгновенного чтения или скачивания:

![Search & Action Cards](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_search_results.png)

Vailib поддерживает **12 языков интерфейса и каталога** (Русский, Английский, Немецкий, Испанский, Французский, Греческий, Арабский, Хинди, Португальский, Китайский, Бенгальский, Нидерландский) с корректной группировкой национальных алфавитов и символов Unicode.

---

### 🤖 5. Telegram-бот: Автоматическое распознавание (OCR) и конвертация
Интегрированный в контейнер Telegram-бот превращает смартфон в портативный сканер книг:
- Отправьте боту PDF-документ или DjVu-скан.
- Фоновый демон выполнит распознавание текста через **Tesseract OCR**, конвертирует документ в аккуратный **EPUB** через Calibre и сразу положит готовую книгу в вашу библиотеку.

---

### ⚙️ 6. Развертывание за 60 секунд: Docker и Setup Wizard
Вся система — веб-сервер, база данных PostgreSQL, фоновый сканер, Telegram-бот и конвертеры — упакована в оптимизированный Docker Compose стек:

![Settings Dashboard](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_settings.png)

#### Установка одной командой на любой Linux / VPS / macOS сервер:
```bash
curl -fsSL https://raw.githubusercontent.com/vikgr/vailibos/main/install.sh | bash
```

После запуска вас встретит удобный 6-шаговый **Setup Wizard**:
1. Проверка прав доступа и окружения.
2. Интерактивный тест записи на диск (`/library`).
3. Подключение и миграции базы данных.
4. Создание администратора.
5. Настройка Telegram-бота (опционально).
6. Автоматическая загрузка стартовой библиотеки классических книг из Project Gutenberg.

---

### 💡 Инженерный опыт: Как мы создавали Vailib с Google Deepmind Antigravity
Проект Vailib v5.0 стал практическим подтверждением колоссального потенциала современных AI-ассистентов в разработке сложного системного ПО:
- **Глубокий рефакторинг**: Переработка устаревшей архитектуры SOPDS в современный реактивный бэкенд на Django и Python 3.10.
- **Frontend & UX**: Разработка с нуля glassmorphic OLED-темы и сверхчистого E-Ink слоя.
- **Docker-контейнеризация**: Сборка мультистейдж-образов с оптимизацией веса слоев, поддержкой OCR-библиотек и демонов синхронизации.
- **AI-first документация**: Создание не только инструкций для пользователей, но и файла `README_AI_CONTEXT.md` — архитектурного манифеста для других AI-агентов, сопровождающих проект.

---

### 🔗 Ссылки и открытый исходный код
Проект распространяется под свободной лицензией **GPL-3.0**.

- 🌟 **GitHub репозиторий**: [https://github.com/vikgr/vailibos](https://github.com/vikgr/vailibos)
- 🚀 **Быстрая установка**: `curl -fsSL https://raw.githubusercontent.com/vikgr/vailibos/main/install.sh | bash`

Ставьте звёзды ⭐ репозиторию, делитесь фидбеком и приятного чтения вашей личной цифровой библиотеки!

---

## 🇬🇧 Full English Article (LinkedIn Articles / Medium / Substack / Dev.to / Reddit)

### Title:
# Re-Engineering the Personal Digital Library: Inside Vailib v5.0 — Built with Google Deepmind Antigravity 📚⚡

![Vailib v5.0 Hero Banner](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_showcase.jpg)

### Introduction: Why Self-Hosted eBook Servers Needed a Reboot
Anyone who has attempted to set up a private digital library server has encountered the same frustrating trade-off.

On one hand, legacy OPDS catalog servers feature interfaces frozen in the mid-2000s. They are difficult to navigate on mobile screens and cause embedded web browsers on E-Ink readers (like Kindle, Kobo, or Onyx Boox) to freeze completely. On the other hand, proprietary cloud reading platforms trap your personal collection behind recurring monthly fees, privacy invasions, and DRM lock-in.

We asked a straightforward question: **What should the ideal personal digital library look like in 2026?**
- It must render any book format (EPUB, FB2, PDF, DjVu) **directly inside the web browser** without requiring third-party reader applications.
- Its interface must be **hardware-aware**: rendering a luxurious obsidian OLED dark theme on monitors and tablets, while instantly serving a razor-sharp 1-bit monochrome layout to E-Ink devices.
- Adding books should be effortless: drop a `.zip` archive containing dozens of files into your browser, and the server automatically extracts, categorizes, and indexes them in seconds.
- On-the-go ingestion: forward a PDF scan to a private Telegram bot, and let background OCR and conversion daemons deliver an optimized EPUB to your bookshelf.

This vision led to **Vailib v5.0 (vailibos)** — a modern, containerized, open-source personal digital library and OPDS ecosystem, engineered end-to-end in pair-programming with **Google Deepmind's Antigravity** (Advanced Agentic AI Coding Assistant).

---

### 🎨 1. Hardware-Aware Dual-Identity UI Architecture
Building a single responsive UI for both high-resolution color screens and reflective electronic paper displays is fundamentally flawed. Subtle drop-shadows, blurs, and animations that look stunning on an iPad Pro turn an E-Ink reader's display into a slow, flashing blur.

![OLED Dark Mode Catalog](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_catalog_dark.png)

Vailib resolves this with a dedicated **Dual-Identity UI Architecture**:

1. **Obsidian OLED Dark Mode (Desktop, Tablets, Mobile)**:
   - Deep obsidian backgrounds optimized for contrast and OLED battery preservation.
   - Frosted glassmorphism panels, glowing neon badges, dynamic book statistics, and smooth transitions.
2. **Pure 1-Bit High-Contrast E-INK Mode (Kindle, Kobo, PocketBook, Onyx Boox, Remarkable)**:
   - Eliminates CSS transitions, translucency, and non-essential JavaScript.
   - High-contrast 1-bit typography and solid structural borders to eliminate e-ink ghosting.
   - Lightning-fast page repaints and minimal memory consumption.

![E-Ink Mode Preview](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_eink_catalog.png)

> **Automatic Hardware Detection:** The server evaluates incoming User-Agent headers and screen rendering metrics upon connection. E-reader devices automatically receive the 1-bit layout, while modern color screens enjoy full glassmorphism. A 1-click manual override switch remains available in the header.

---

### 📖 2. Universal In-Browser Reader with Full Keyboard Navigation
Reading on Vailib is frictionless across four primary eBook formats:

![In-Browser Book Reader](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_reader_epub.png)

- **EPUB**: Rendered via an optimized ePub.js stream with single-column pagination, chapter jumping, and preserved stylesheets.
- **FB2**: High-speed native XML DOM parser preserving section hierarchies, notes, and epigraphs.
- **PDF**: Crisp canvas rendering powered by PDF.js.
- **DjVu**: Client-side decoding powered by DjVu.js.

#### ⌨️ Full Keyboard Navigation:
- **Next Page**: `Right Arrow` (`→`), `Space`, `Page Down` (`PgDn`), `Down Arrow` (`↓`)
- **Previous Page**: `Left Arrow` (`←`), `Page Up` (`PgUp`), `Shift + Space`, `Up Arrow` (`↑`)

Readers can customize typography on the fly: adjust font size (12px to 28px), select typefaces (*Serif, Sans-Serif, OpenDyslexic, Monospace*), and toggle reading palettes (*OLED Dark, Paper Sepia, Light, E-Ink*).

---

### 📤 3. Drag & Drop Upload with Smart Multi-Book ZIP Extraction
Adding new titles to a self-hosted library no longer requires terminal sessions or complex volume mounts:

![Drag & Drop Upload & ZIP Extractor](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_upload_view.png)

1. Open the **Populate & Upload** dashboard (`/web/populate/`).
2. Drag and drop single files or bulk batches (`.epub`, `.pdf`, `.fb2`, `.mobi`, `.djvu`, `.cbr`, `.cbz`, `.azw3`, `.txt`, `.docx`).
3. **Smart ZIP Extraction**: Drop a `.zip` archive containing dozens of nested books; Vailib safely unzips them with built-in *Zip Slip* directory traversal security.
4. **Instant File Watcher**: A background file-system watcher detects new books and completes database indexing in under 5 seconds.
5. Supports large scanned volumes and archives up to **1 GB per upload**.

---

### 🔍 4. Search, Categorization & 12-Language Global Matrix
Search instantly across titles, authors, genres, and series with rich interactive cards:

![Search & Action Cards](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_search_results.png)

Vailib includes native support for **12 major languages** with Unicode script grouping (Latin, Cyrillic, Greek, Arabic, Devanagari, Bengali, Hanzi). It also connects seamlessly with mobile OPDS reading apps like KyBook, Moon+ Reader, FBReader, and Aldiko.

---

### 🤖 5. Telegram Document Bot: Automated OCR & Conversion
Vailib includes an integrated Telegram daemon:
- Forward research papers, scans, or raw documents to your private Telegram bot.
- The server automatically triggers **Tesseract OCR** for text recognition, converts the document into standard **EPUB** format via Calibre, and places the book directly onto your shelf.

---

### ⚙️ 6. 60-Second Universal Deployment via Docker
The entire ecosystem — Django web server, PostgreSQL database, background scanner, Telegram daemon, and conversion tools — runs as a single, highly optimized Docker Compose deployment:

![Settings Dashboard](https://raw.githubusercontent.com/vikgr/vailibos/main/docs/images/vailib_real_settings.png)

#### Install on any Linux, VPS, Raspberry Pi, or macOS machine:
```bash
curl -fsSL https://raw.githubusercontent.com/vikgr/vailibos/main/install.sh | bash
```

Upon startup, a guided 6-step **Web Setup Wizard** verifies storage write permissions, sets up database migrations, configures your administrator credentials, and bootstraps classic literature from Project Gutenberg.

---

### 💡 The Future of Agentic AI Engineering: Built with Antigravity
Co-developing Vailib v5.0 with **Google Deepmind Antigravity** provided firsthand insight into the future of software engineering:
- Autonomous refactoring of legacy Django and Python codebases into modular, robust components.
- Rapid authoring of clean glassmorphic CSS, responsive UI modules, and headless browser validation tests.
- Generation of human-centric and AI-agent-specific architectural documentation.

---

### 🌟 Open Source & Available Now on GitHub
Vailib is 100% free and open source under the **GPL-3.0** license.

- 📦 **GitHub Repository**: [https://github.com/vikgr/vailibos](https://github.com/vikgr/vailibos)
- ⚡ **One-Line Install**: `curl -fsSL https://raw.githubusercontent.com/vikgr/vailibos/main/install.sh | bash`

Star the repository ⭐ on GitHub, spin it up on your server, and enjoy reading your private library anywhere!

---

#OpenSource #SelfHosted #HomeLab #Docker #DigitalLibrary #eBook #EInk #Kindle #Python #Django #Antigravity #GoogleDeepmind #AI
