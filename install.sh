#!/usr/bin/env bash
# ==============================================================================
#  📚 VAILIB OPEN SOURCE (vailibos) - Universal Automated Installer
#  Compatible with Ubuntu, Debian, CentOS, AlmaLinux, Rocky, Alpine, Arch, macOS
# ==============================================================================
#  One-line install:
#    curl -fsSL https://raw.githubusercontent.com/vikgr/vailibos/main/install.sh | bash
# ==============================================================================

set -eo pipefail

# Text formatting & Colors
BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear 2>/dev/null || true
echo -e "${BLUE}${BOLD}"
cat << 'EOF'
  __      __     _____ _      _____ ____   ____   _____ 
  \ \    / /\   |_   _| |    |_   _|  _ \ / __ \ / ____|
   \ \  / /  \    | | | |      | | | |_) | |  | | (___  
    \ \/ / /\ \   | | | |      | | |  _ <| |  | |\___ \ 
     \  / ____ \ _| |_| |____ _| |_| |_) | |__| |____) |
      \/_/    \_\_____|______|_____|____/ \____/|_____/ 
EOF
echo -e "${CYAN}   🚀 The Ultimate Digital Library & OPDS Ecosystem (v5.0)${NC}\n"
echo -e "${BLUE}=====================================================================${NC}\n"

# Check sudo / root access
SUDO=""
if [ "$EUID" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
    else
        echo -e "${RED}❌ Error: This installer requires root or sudo privileges.${NC}"
        exit 1
    fi
fi

# Detect Server IP
SERVER_IP=""
if command -v hostname >/dev/null 2>&1; then
    SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || true)
fi
if [ -z "$SERVER_IP" ] && command -v ip >/dev/null 2>&1; then
    SERVER_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7}' || true)
fi
[ -z "$SERVER_IP" ] && SERVER_IP="127.0.0.1"

# Step 1: Detect & Install Dependencies
echo -e "${CYAN}${BOLD}[1/5] Checking and installing system dependencies...${NC}"

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

# Ensure Git
if ! command -v git >/dev/null 2>&1; then
    echo -e "  ${YELLOW}➜ Git not found. Installing git...${NC}"
    install_pkg git
fi
echo -e "  ${GREEN}✔ Git is installed.${NC}"

# Ensure Docker
if ! command -v docker >/dev/null 2>&1; then
    echo -e "  ${YELLOW}➜ Docker not found. Installing Docker engine...${NC}"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL https://get.docker.com | $SUDO sh
    else
        install_pkg curl
        curl -fsSL https://get.docker.com | $SUDO sh
    fi
fi

# Ensure Docker daemon is started
if command -v systemctl >/dev/null 2>&1; then
    $SUDO systemctl enable --now docker >/dev/null 2>&1 || true
    $SUDO systemctl start docker >/dev/null 2>&1 || true
elif command -v service >/dev/null 2>&1; then
    $SUDO service docker start >/dev/null 2>&1 || true
fi
echo -e "  ${GREEN}✔ Docker engine is active.${NC}"

# Determine Compose Command
DOCKER_COMPOSE=""
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "  ${YELLOW}➜ Docker Compose not found. Installing docker-compose-plugin...${NC}"
    install_pkg docker-compose-plugin || install_pkg docker-compose || true
    if docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker-compose"
    else
        echo -e "${RED}❌ Failed to install Docker Compose. Please install Docker Compose manually and re-run.${NC}"
        exit 1
    fi
fi
echo -e "  ${GREEN}✔ Docker Compose is ready (${DOCKER_COMPOSE}).${NC}"

# Step 2: Destination Setup & Repository Clone
echo -e "\n${CYAN}${BOLD}[2/5] Setting up repository workspace...${NC}"

CURRENT_DIR=$(pwd)
IS_INSIDE_REPO=false
if [ -f "$CURRENT_DIR/Dockerfile_vailib" ] && [ -f "$CURRENT_DIR/views.py" ]; then
    IS_INSIDE_REPO=true
    TARGET_DIR="$CURRENT_DIR"
    echo -e "  ${GREEN}✔ Running inside existing Vailib repository at: ${BOLD}$TARGET_DIR${NC}"
else
    DEFAULT_DIR="$HOME/vailibos"
    read -rp "  📂 Installation directory [$DEFAULT_DIR]: " INPUT_DIR
    TARGET_DIR="${INPUT_DIR:-$DEFAULT_DIR}"
    
    if [ ! -d "$TARGET_DIR/.git" ]; then
        echo -e "  ⬇️  Cloning vailibos into ${BOLD}$TARGET_DIR${NC}..."
        mkdir -p "$TARGET_DIR"
        git clone https://github.com/vikgr/vailibos.git "$TARGET_DIR"
    else
        echo -e "  🔄 Updating existing repository at ${BOLD}$TARGET_DIR${NC}..."
        (cd "$TARGET_DIR" && git pull origin main || true)
    fi
fi

cd "$TARGET_DIR"

# Step 3: Interactive Configuration
echo -e "\n${CYAN}${BOLD}[3/5] Configuration & Environment Settings...${NC}"

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

# Detect system timezone
SYSTEM_TZ="Europe/Madrid"
if [ -f /etc/timezone ]; then
    SYSTEM_TZ=$(cat /etc/timezone | tr -d ' \n\r')
elif [ -h /etc/localtime ]; then
    SYSTEM_TZ=$(readlink /etc/localtime | sed 's|.*/zoneinfo/||')
fi

# Prompt Port
DEF_PORT="${EXISTING_PORT:-8081}"
read -rp "  🌐 Web Access Port [$DEF_PORT]: " CFG_PORT
CFG_PORT="${CFG_PORT:-$DEF_PORT}"

# Prompt Books Folder
DEF_BOOKS="${EXISTING_BOOKS:-$TARGET_DIR/books}"
read -rp "  📚 Books collection folder path [$DEF_BOOKS]: " CFG_BOOKS
CFG_BOOKS="${CFG_BOOKS:-$DEF_BOOKS}"

# Prompt Timezone
DEF_TZ="${EXISTING_TZ:-$SYSTEM_TZ}"
read -rp "  🕒 Server Timezone [$DEF_TZ]: " CFG_TZ
CFG_TZ="${CFG_TZ:-$DEF_TZ}"

# Prompt Database Password
if [ -n "$EXISTING_PASS" ]; then
    DEF_PASS="$EXISTING_PASS"
else
    DEF_PASS=$(openssl rand -hex 12 2>/dev/null || echo "vailib_db_$(date +%s)")
fi
read -rp "  🔑 Database Password [$DEF_PASS]: " CFG_PASS
CFG_PASS="${CFG_PASS:-$DEF_PASS}"

# Optional Telegram Bot Token
DEF_TOKEN="${EXISTING_TOKEN:-}"
read -rp "  🤖 Telegram Bot Token (optional, press Enter to skip) [$DEF_TOKEN]: " CFG_TOKEN
CFG_TOKEN="${CFG_TOKEN:-$DEF_TOKEN}"

DEF_CHAT="${EXISTING_CHAT:-}"
if [ -n "$CFG_TOKEN" ]; then
    read -rp "  👤 Allowed Telegram Chat ID (optional) [$DEF_CHAT]: " CFG_CHAT
    CFG_CHAT="${CFG_CHAT:-$DEF_CHAT}"
else
    CFG_CHAT=""
fi

# Step 4: Write .env & Create Host Storage
echo -e "\n${CYAN}${BOLD}[4/5] Preparing storage and environment files...${NC}"

# Resolve paths
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

echo -e "  ${GREEN}✔ Configuration saved to .env${NC}"
echo -e "  ${GREEN}✔ Host directories created and permissions set.${NC}"

# Step 5: Build & Launch Containers
echo -e "\n${CYAN}${BOLD}[5/5] Building and launching Docker container stack...${NC}"

$DOCKER_COMPOSE up -d --build

echo -e "\n  ⏳ Waiting for database and services to initialize..."
sleep 5

echo -e "\n${GREEN}${BOLD}=====================================================================${NC}"
echo -e "${GREEN}${BOLD}🎉 VAILIB INSTALLATION COMPLETED SUCCESSFULLY!${NC}"
echo -e "${GREEN}${BOLD}=====================================================================${NC}\n"

echo -e "  📖 ${BOLD}Digital Library Web UI:${NC}    ${YELLOW}http://${SERVER_IP}:${CFG_PORT}/web/${NC}"
echo -e "  🧙 ${BOLD}Interactive Setup Wizard:${NC}  ${CYAN}http://${SERVER_IP}:${CFG_PORT}/web/setup/${NC}"
echo -e "  📁 ${BOLD}Local Books Directory:${NC}     ${PURPLE}${CFG_BOOKS}${NC}"
echo -e "  🛠️  ${BOLD}Constance Admin Panel:${NC}     ${YELLOW}http://${SERVER_IP}:${CFG_PORT}/admin/${NC}"

echo -e "\n${BOLD}Quick Management Commands:${NC}"
echo -e "  • Check logs:     ${CYAN}cd ${TARGET_DIR} && ${DOCKER_COMPOSE} logs -f app${NC}"
echo -e "  • Restart stack:  ${CYAN}cd ${TARGET_DIR} && ${DOCKER_COMPOSE} restart${NC}"
echo -e "  • Stop library:   ${CYAN}cd ${TARGET_DIR} && ${DOCKER_COMPOSE} down${NC}"
echo -e "  • Start library:  ${CYAN}cd ${TARGET_DIR} && ${DOCKER_COMPOSE} up -d${NC}"

echo -e "\n${GREEN}👉 Open ${CYAN}http://${SERVER_IP}:${CFG_PORT}/web/setup/${GREEN} in your browser to finalize your administrator setup!${NC}\n"
