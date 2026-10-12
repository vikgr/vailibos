#!/usr/bin/env bash
# ==============================================================================
#  📚 VAILIB (vailibos) - Interactive Setup & Installation Wizard
#  KIAUH-style, beginner-friendly TUI installer
# ==============================================================================

set -eo pipefail

# ── Color Palette & Styles ────────────────────────────────────────────────────
BOLD='\033[1m'
DIM='\033[2m'
ITALIC='\033[3m'
UNDERLINE='\033[4m'

# Foreground colors
RED='\033[38;5;196m'
GREEN='\033[38;5;48m'
YELLOW='\033[38;5;220m'
BLUE='\033[38;5;75m'
PURPLE='\033[38;5;141m'
CYAN='\033[38;5;51m'
WHITE='\033[38;5;255m'
GRAY='\033[38;5;244m'
DARKGRAY='\033[38;5;238m'

# Badges & Inverted
BG_CYAN='\033[48;5;31m\033[38;5;255m'
BG_GREEN='\033[48;5;28m\033[38;5;255m'
BG_YELLOW='\033[48;5;178m\033[38;5;16m'
BG_PURPLE='\033[48;5;98m\033[38;5;255m'

NC='\033[0m' # No Color

# ── UI Helper Functions ───────────────────────────────────────────────────────

clear_screen() {
    clear 2>/dev/null || true
}

print_header() {
    clear_screen
    echo -e "${CYAN}${BOLD}"
    cat << 'EOF'
  __      __     _____ _      _____ ____   ____   _____ 
  \ \    / /\   |_   _| |    |_   _|  _ \ / __ \ / ____|
   \ \  / /  \    | | | |      | | | |_) | |  | | (___  
    \ \/ / /\ \   | | | |      | | |  _ <| |  | |\___ \ 
     \  / ____ \ _| |_| |____ _| |_| |_) | |__| |____) |
      \/_/    \_\_____|______|_____|____/ \____/|_____/ 
EOF
    echo -e "${PURPLE}  ── 📖 The Ultimate Digital Library & OPDS Ecosystem (v5.0) ──${NC}"
    echo -e "${DARKGRAY}───────────────────────────────────────────────────────────────────────────────${NC}"
}

print_step() {
    local num="$1"
    local total="$2"
    local title="$3"
    echo -e "\n${BG_CYAN} STEP ${num}/${total} ${NC} ${BOLD}${WHITE}${title}${NC}"
    echo -e "${DARKGRAY}───────────────────────────────────────────────────────────────────────────────${NC}"
}

info_box() {
    local text="$1"
    echo -e "${BLUE}ℹ️  ${DIM}${text}${NC}"
}

tip_box() {
    local text="$1"
    echo -e "${YELLOW}💡 ${BOLD}Подсказка:${NC} ${DIM}${text}${NC}"
}

success_box() {
    local text="$1"
    echo -e "${GREEN}✔ ${text}${NC}"
}

warn_box() {
    local text="$1"
    echo -e "${YELLOW}⚠️  ${text}${NC}"
}

error_box() {
    local text="$1"
    echo -e "${RED}✖ ${text}${NC}"
}

pause_prompt() {
    echo ""
    read -rp "  Нажмите [Enter], чтобы продолжить..." dummy
}

# ── Detect Privilege / sudo ───────────────────────────────────────────────────
SUDO=""
if [ "$EUID" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
    else
        print_header
        error_box "Для установки требуются права root или sudo."
        exit 1
    fi
fi

# ── Detect Server IP ──────────────────────────────────────────────────────────
SERVER_IP=""
if command -v hostname >/dev/null 2>&1; then
    SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || true)
fi
if [ -z "$SERVER_IP" ] && command -v ip >/dev/null 2>&1; then
    SERVER_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7}' || true)
fi
[ -z "$SERVER_IP" ] && SERVER_IP="127.0.0.1"

# ── Detect System Timezone ────────────────────────────────────────────────────
SYSTEM_TZ="Europe/Madrid"
if [ -f /etc/timezone ]; then
    SYSTEM_TZ=$(cat /etc/timezone | tr -d ' \n\r')
elif [ -h /etc/localtime ]; then
    SYSTEM_TZ=$(readlink /etc/localtime | sed 's|.*/zoneinfo/||')
fi

# ── Package Installer ─────────────────────────────────────────────────────────
install_pkg() {
    local pkg="$1"
    if command -v apt-get >/dev/null 2>&1; then
        $SUDO apt-get update -qq && $SUDO apt-get install -y -qq "$pkg"
    elif command -v dnf >/dev/null 2>&1; then
        $SUDO dnf install -y -q "$pkg"
    elif command -v yum >/dev/null 2>&1; then
        $SUDO yum install -y -q "$pkg"
    elif command -v pacman >/dev/null 2>&1; then
        $SUDO pacman -Sy --noconfirm "$pkg"
    elif command -v apk >/dev/null 2>&1; then
        $SUDO apk add --no-cache "$pkg"
    elif command -v brew >/dev/null 2>&1; then
        brew install "$pkg"
    fi
}

# ── Welcome & Interactive Mode Selection ──────────────────────────────────────
print_header

echo -e "\n${BOLD}${WHITE}Добро пожаловать в мастер установки библиотеки Vailib!${NC}"
echo -e "${GRAY}Этот пошаговый мастер поможет настроить и запустить вашу личную библиотеку,${NC}"
echo -e "${GRAY}веб-читалку (EPUB/PDF/FB2/DjVu), OPDS-каталог и Telegram-бота.${NC}\n"

echo -e "  ${CYAN}${BOLD}[1]${NC} 🚀 ${BOLD}Быстрая экспресс-установка (Рекомендуется)${NC}"
echo -e "      ${DIM}Оптимальные параметры по умолчанию. Ничего сложного, старт за 1 минуту.${NC}\n"

echo -e "  ${PURPLE}${BOLD}[2]${NC} 🛠️  ${BOLD}Пошаговая настройка (Экспертный режим)${NC}"
echo -e "      ${DIM}Выбор портов, папки для книг, интеграции Telegram-бота и паролей.${NC}\n"

echo -e "  ${YELLOW}${BOLD}[3]${NC} 🔄 ${BOLD}Только перезапуск / обновление существующих контейнеров${NC}\n"

echo -e "  ${RED}${BOLD}[Q]${NC} Выход из мастера\n"

SETUP_MODE=""
while true; do
    read -rp "  👉 Выберите вариант [1-3, или Q]: " USER_CHOICE
    case "$USER_CHOICE" in
        1|"")
            SETUP_MODE="express"
            break
            ;;
        2)
            SETUP_MODE="custom"
            break
            ;;
        3)
            SETUP_MODE="restart_only"
            break
            ;;
        [qQ])
            echo -e "\n${YELLOW}Установка отменена пользователем. До свидания!${NC}"
            exit 0
            ;;
        *)
            warn_box "Пожалуйста, введите 1, 2, 3 или Q."
            ;;
    esac
done

# ── Step 1: Dependencies ──────────────────────────────────────────────────────
print_header
print_step "1" "5" "Проверка и установка системных зависимостей"

echo -e "  Проверяем наличие Git, Docker и Docker Compose...\n"

# Git
if ! command -v git >/dev/null 2>&1; then
    echo -e "  ${YELLOW}➜ Git не найден. Устанавливаем Git...${NC}"
    install_pkg git
fi
success_box "Git установлен и готов."

# Docker
if ! command -v docker >/dev/null 2>&1; then
    echo -e "  ${YELLOW}➜ Docker не найден. Загружаем официальный Docker Engine...${NC}"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL https://get.docker.com | $SUDO sh
    else
        install_pkg curl
        curl -fsSL https://get.docker.com | $SUDO sh
    fi
fi

# Docker Daemon
if command -v systemctl >/dev/null 2>&1; then
    $SUDO systemctl enable --now docker >/dev/null 2>&1 || true
    $SUDO systemctl start docker >/dev/null 2>&1 || true
elif command -v service >/dev/null 2>&1; then
    $SUDO service docker start >/dev/null 2>&1 || true
fi
success_box "Docker Engine активен и запущен."

# Compose
DOCKER_COMPOSE=""
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "  ${YELLOW}➜ Docker Compose не найден. Устанавливаем плагин Compose...${NC}"
    install_pkg docker-compose-plugin || install_pkg docker-compose || true
    if docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker-compose"
    else
        error_box "Не удалось установить Docker Compose. Установите его вручную."
        exit 1
    fi
fi
success_box "Docker Compose готов к работе (${DOCKER_COMPOSE})."

sleep 1

# ── Step 2: Destination Setup & Repository Clone ──────────────────────────────
print_header
print_step "2" "5" "Размещение рабочей директории"

CURRENT_DIR=$(pwd)
IS_INSIDE_REPO=false
if [ -f "$CURRENT_DIR/Dockerfile_vailib" ] && [ -f "$CURRENT_DIR/views.py" ]; then
    IS_INSIDE_REPO=true
    TARGET_DIR="$CURRENT_DIR"
    success_box "Мастер запущен непосредственно из репозитория: ${BOLD}${TARGET_DIR}${NC}"
else
    DEFAULT_DIR="$HOME/vailibos"
    if [ "$SETUP_MODE" == "express" ]; then
        TARGET_DIR="$DEFAULT_DIR"
        info_box "Используется стандартный путь: ${BOLD}${TARGET_DIR}${NC}"
    else
        tip_box "В этой папке будут храниться конфигурационные файлы и проект."
        read -rp "  📂 Папка для установки [$DEFAULT_DIR]: " INPUT_DIR
        TARGET_DIR="${INPUT_DIR:-$DEFAULT_DIR}"
    fi

    if [ ! -d "$TARGET_DIR/.git" ]; then
        echo -e "  ⬇️  Клонируем репозиторий vailibos в ${BOLD}$TARGET_DIR${NC}..."
        mkdir -p "$TARGET_DIR"
        git clone https://github.com/vikgr/vailibos.git "$TARGET_DIR"
    else
        echo -e "  🔄 Обновляем существующий репозиторий в ${BOLD}$TARGET_DIR${NC}..."
        (cd "$TARGET_DIR" && git pull origin main || true)
    fi
fi

cd "$TARGET_DIR"
sleep 1

# If user chose only restart/update
if [ "$SETUP_MODE" == "restart_only" ]; then
    print_header
    echo -e "\n${CYAN}${BOLD}Перезапуск и обновление контейнеров...${NC}\n"
    $DOCKER_COMPOSE down 2>/dev/null || true
    $DOCKER_COMPOSE up -d --build
    echo -e "\n${GREEN}${BOLD}✔ Контейнеры успешно обновлены и перезапущены!${NC}\n"
    exit 0
fi

# ── Step 3: Interactive Configuration ─────────────────────────────────────────
print_header
print_step "3" "5" "Настройка параметров библиотеки"

# Read existing .env if present
EXISTING_PORT=""
EXISTING_BOOKS=""
EXISTING_PASS=""
EXISTING_TZ=""
EXISTING_TOKEN=""
EXISTING_CHAT=""

if [ -f ".env" ]; then
    EXISTING_PORT=$(grep -E "^PORT=" .env | cut -d'=' -f2- || true)
    EXISTING_BOOKS=$(grep -E "^BOOKS_PATH=" .env | cut -d'=' -f2- || true)
    EXISTING_PASS=$(grep -E "^DB_PASSWORD=" .env | cut -d'=' -f2- || true)
    EXISTING_TZ=$(grep -E "^TIME_ZONE=" .env | cut -d'=' -f2- || true)
    EXISTING_TOKEN=$(grep -E "^BOT_TOKEN=" .env | cut -d'=' -f2- || true)
    EXISTING_CHAT=$(grep -E "^CHAT_ID=" .env | cut -d'=' -f2- || true)
fi

DEF_PORT="${EXISTING_PORT:-8081}"
DEF_BOOKS="${EXISTING_BOOKS:-$TARGET_DIR/books}"
DEF_TZ="${EXISTING_TZ:-$SYSTEM_TZ}"

if [ -n "$EXISTING_PASS" ]; then
    DEF_PASS="$EXISTING_PASS"
else
    DEF_PASS=$(openssl rand -hex 12 2>/dev/null || echo "vailib_db_$(date +%s)")
fi

DEF_TOKEN="${EXISTING_TOKEN:-}"
DEF_CHAT="${EXISTING_CHAT:-}"

if [ "$SETUP_MODE" == "express" ]; then
    # Express mode defaults
    CFG_PORT="$DEF_PORT"
    CFG_BOOKS="$DEF_BOOKS"
    CFG_TZ="$DEF_TZ"
    CFG_PASS="$DEF_PASS"
    CFG_TOKEN="$DEF_TOKEN"
    CFG_CHAT="$DEF_CHAT"

    echo -e "  Применены рекомендуемые настройки для быстрого старта:\n"
    echo -e "  • Веб-порт:        ${YELLOW}${CFG_PORT}${NC}"
    echo -e "  • Папка для книг:   ${PURPLE}${CFG_BOOKS}${NC}"
    echo -e "  • Часовой пояс:     ${BLUE}${CFG_TZ}${NC}"
    echo -e "  • Пароль базы:      ${GRAY}[сгенерирован безопасно]${NC}"
    if [ -n "$CFG_TOKEN" ]; then
        echo -e "  • Telegram Bot:    ${GREEN}Сохранен из предыдущей конфигурации${NC}"
    else
        echo -e "  • Telegram Bot:    ${GRAY}Не настроен (можно добавить позже в меню)${NC}"
    fi
    echo ""
    tip_box "Все эти параметры можно в любой момент изменить через веб-интерфейс или файл .env."
    sleep 2
else
    # Custom / Detailed wizard mode
    tip_box "Порт, по которому веб-интерфейс будет открываться в браузере."
    read -rp "  🌐 Веб-порт библиотеки [$DEF_PORT]: " INPUT_PORT
    CFG_PORT="${INPUT_PORT:-$DEF_PORT}"
    echo ""

    tip_box "Папка на вашем сервере/диске, где лежат или будут лежать ваши книги (PDF, EPUB, FB2, DjVu)."
    echo -e "     ${DIM}Например: /mnt/storage/books или $DEF_BOOKS${NC}"
    read -rp "  📚 Путь к папке с книгами [$DEF_BOOKS]: " INPUT_BOOKS
    CFG_BOOKS="${INPUT_BOOKS:-$DEF_BOOKS}"
    echo ""

    tip_box "Часовой пояс для корректного отображения времени добавления книг."
    read -rp "  🕒 Часовой пояс сервера [$DEF_TZ]: " INPUT_TZ
    CFG_TZ="${INPUT_TZ:-$DEF_TZ}"
    echo ""

    tip_box "Пароль для внутренней базы данных PostgreSQL."
    read -rp "  🔑 Пароль базы данных [$DEF_PASS]: " INPUT_PASS
    CFG_PASS="${INPUT_PASS:-$DEF_PASS}"
    echo ""

    echo -e "${DARKGRAY}───────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "  🤖 ${BOLD}Telegram-бот ассистент (Опционально)${NC}"
    echo -e "  ${DIM}Бот позволяет отправлять книги прямо в чат Telegram для конвертации и загрузки.${NC}\n"
    read -rp "  👉 Настроить Telegram-бота прямо сейчас? [y/N]: " WANT_BOT
    if [[ "$WANT_BOT" =~ ^[yYдД] ]]; then
        tip_box "Токен получается у @BotFather в Telegram."
        read -rp "  🤖 Токен Telegram бота [$DEF_TOKEN]: " INPUT_TOKEN
        CFG_TOKEN="${INPUT_TOKEN:-$DEF_TOKEN}"

        tip_box "Ваш персональный Telegram Chat ID для ограничения доступа (можно узнать у @userinfobot)."
        read -rp "  👤 Разрешенный Telegram Chat ID (опционально) [$DEF_CHAT]: " INPUT_CHAT
        CFG_CHAT="${INPUT_CHAT:-$DEF_CHAT}"
    else
        CFG_TOKEN="$DEF_TOKEN"
        CFG_CHAT="$DEF_CHAT"
    fi
fi

# ── Summary Confirmation ──────────────────────────────────────────────────────
print_header
echo -e "\n${BOLD}${WHITE}📋 Проверьте выбранные параметры перед запуском:${NC}\n"
echo -e "  ┌─────────────────────────┬─────────────────────────────────────────────────┐"
printf "  │ %-23s │ %-47s │\n" "Параметр" "Значение"
echo -e "  ├─────────────────────────┼─────────────────────────────────────────────────┤"
printf "  │ %-23s │ %-47s │\n" "🌐 Веб-порт" "$CFG_PORT"
printf "  │ %-23s │ %-47s │\n" "📚 Папка книг" "$CFG_BOOKS"
printf "  │ %-23s │ %-47s │\n" "🕒 Часовой пояс" "$CFG_TZ"
printf "  │ %-23s │ %-47s │\n" "🔑 Пароль БД" "******** (скрыт)"
if [ -n "$CFG_TOKEN" ]; then
printf "  │ %-23s │ %-47s │\n" "🤖 Telegram-бот" "Включен"
else
printf "  │ %-23s │ %-47s │\n" "🤖 Telegram-бот" "Отключен"
fi
echo -e "  └─────────────────────────┴─────────────────────────────────────────────────┘\n"

read -rp "  👉 Всё верно? Начать установку и запуск? [Y/n]: " CONFIRM_LAUNCH
if [[ "$CONFIRM_LAUNCH" =~ ^[nNнН] ]]; then
    warn_box "Установка прервана. Вы можете запустить мастер заново в любой момент."
    exit 0
fi

# ── Step 4: Write .env & Create Host Storage ──────────────────────────────────
print_header
print_step "4" "5" "Подготовка хранилища и файлов окружения"

echo -e "  Создаем каталоги и сохраняем переменные в .env...\n"

mkdir -p "$CFG_BOOKS" "$TARGET_DIR/data/sopds" "$TARGET_DIR/data/postgres"
chmod 777 "$CFG_BOOKS" 2>/dev/null || true
touch "$CFG_BOOKS/.trigger_scan" 2>/dev/null || true

cat <<EOF > "$TARGET_DIR/.env"
# ============================================================
# Vailib Open Source Configuration - Generated by install.sh
# ============================================================
PORT=$CFG_PORT
POSTGRES_USER=sopds
POSTGRES_DB=sopds
DB_PASSWORD=$CFG_PASS
TIME_ZONE=$CFG_TZ
BOOKS_PATH=$CFG_BOOKS
DATA_PATH=$TARGET_DIR/data/sopds
DB_DATA_PATH=$TARGET_DIR/data/postgres
BOT_TOKEN=$CFG_TOKEN
CHAT_ID=$CFG_CHAT
EOF

success_box "Конфигурация успешно сохранена в: ${BOLD}${TARGET_DIR}/.env${NC}"
success_box "Папки данных подготовлены с корректными правами доступа."
sleep 1

# ── Step 5: Build & Launch Containers ─────────────────────────────────────────
print_header
print_step "5" "5" "Сборка и запуск Docker-стека"

echo -e "  Запускаем контейнеры базы данных PostgreSQL и приложения Vailib...\n"
$DOCKER_COMPOSE up -d --build

echo -e "\n  ⏳ Ожидаем инициализации базы данных и сервисов..."
sleep 5

# ── Final Congratulation Banner ───────────────────────────────────────────────
print_header

echo -e "\n${BG_GREEN} ПОЗДРАВЛЯЕМ! ${NC} ${BOLD}${GREEN}УСТАНОВКА VAILIB УСПЕШНО ЗАВЕРШЕНА! 🎉${NC}\n"

echo -e "  Ваша домашняя цифровая библиотека готова к использованию:\n"

echo -e "  📖 ${BOLD}Веб-интерфейс каталога:${NC}    ${CYAN}http://${SERVER_IP}:${CFG_PORT}/web/${NC}"
echo -e "  🧙 ${BOLD}Веб-мастер первого входа:${NC}   ${YELLOW}http://${SERVER_IP}:${CFG_PORT}/web/setup/${NC}"
echo -e "  📁 ${BOLD}Папка с вашими книгами:${NC}     ${PURPLE}${CFG_BOOKS}${NC}"
echo -e "  ⚙️  ${BOLD}Панель администратора:${NC}      ${WHITE}http://${SERVER_IP}:${CFG_PORT}/admin/${NC}\n"

echo -e "${DARKGRAY}───────────────────────────────────────────────────────────────────────────────${NC}"
echo -e "${BOLD}Полезные консольные команды для управления:${NC}"
echo -e "  • Смотреть логи:       ${CYAN}cd ${TARGET_DIR} && ${DOCKER_COMPOSE} logs -f app${NC}"
echo -e "  • Перезапустить:       ${CYAN}cd ${TARGET_DIR} && ${DOCKER_COMPOSE} restart${NC}"
echo -e "  • Остановить библиотеку:${CYAN}cd ${TARGET_DIR} && ${DOCKER_COMPOSE} down${NC}"
echo -e "  • Запустить библиотеку: ${CYAN}cd ${TARGET_DIR} && ${DOCKER_COMPOSE} up -d${NC}"
echo -e "${DARKGRAY}───────────────────────────────────────────────────────────────────────────────${NC}\n"

tip_box "Скопируйте ссылку ${BOLD}http://${SERVER_IP}:${CFG_PORT}/web/setup/${NC}${YELLOW} в браузер, чтобы создать администратора и начать читать!${NC}\n"
