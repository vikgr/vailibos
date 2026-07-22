#!/bin/bash
# Vailib Interactive Installer
# Usage: curl -sSL https://raw.githubusercontent.com/vikgr/vailib/main/install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================${NC}"
echo -e "${CYAN}             📚 VAILIB INSTALLATION WIZARD 📚           ${NC}"
echo -e "${BLUE}========================================================${NC}"

# Check sudo privileges
SUDO=""
if [ "$EUID" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
    else
        echo -e "${RED}❌ Error: This script must be run as root or with a user that has sudo privileges.${NC}"
        exit 1
    fi
fi

# Detect system IP
SYS_IP=$(hostname -I | awk '{print $1}')
[ -z "$SYS_IP" ] && SYS_IP="localhost"

# 1. Dependency Checks
echo -e "\n${CYAN}🔎 Checking system dependencies...${NC}"
for cmd in git docker; do
    if ! command -v $cmd >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Dependency missing: $cmd${NC}"
        echo -e "Attempting to install $cmd..."
        if [ "$cmd" = "git" ]; then
            $SUDO apt-get update && $SUDO apt-get install -y git || { echo -e "${RED}❌ Failed to install git. Please install it manually.${NC}"; exit 1; }
        elif [ "$cmd" = "docker" ]; then
            curl -fsSL https://get.docker.com | sh || { echo -e "${RED}❌ Failed to install Docker. Please install it manually.${NC}"; exit 1; }
        fi
    else
        echo -e "  ✅ $cmd is installed."
    fi
done

# Docker Compose check
if ! docker compose version >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker Compose missing.${NC}"
    echo -e "Installing docker-compose-plugin..."
    $SUDO apt-get update && $SUDO apt-get install -y docker-compose-plugin || { echo -e "${RED}❌ Failed to install Docker Compose. Please install it manually.${NC}"; exit 1; }
else
    echo -e "  ✅ Docker Compose is installed."
fi

# 2. Interactive Prompts
echo -e "\n${CYAN}⚙️  Configuring directories & credentials...${NC}"

# Paths
DEFAULT_REPO_PATH="/home/$(whoami)/vailib"
read -p "📂 Repository path [$DEFAULT_REPO_PATH]: " REPO_PATH
REPO_PATH="${REPO_PATH:-$DEFAULT_REPO_PATH}"

DEFAULT_COMPOSE_PATH="/DATA/AppData/sopds"
read -p "🐳 Production compose path [$DEFAULT_COMPOSE_PATH]: " COMPOSE_PATH
COMPOSE_PATH="${COMPOSE_PATH:-$DEFAULT_COMPOSE_PATH}"

DEFAULT_BOOKS_PATH="/DATA/Downloads/books"
read -p "📚 Books storage mount path [$DEFAULT_BOOKS_PATH]: " BOOKS_PATH
BOOKS_PATH="${BOOKS_PATH:-$DEFAULT_BOOKS_PATH}"

# Check for existing .env in REPO_PATH or production compose path
EXISTING_TOKEN=""
EXISTING_CHAT=""
EXISTING_DB_PASS=""

ENV_SOURCE=""
if [ -f "$REPO_PATH/.env" ]; then
    ENV_SOURCE="$REPO_PATH/.env"
elif [ -f "$COMPOSE_PATH/.env" ]; then
    ENV_SOURCE="$COMPOSE_PATH/.env"
fi

if [ -n "$ENV_SOURCE" ]; then
    EXISTING_TOKEN=$(grep -E "^BOT_TOKEN=" "$ENV_SOURCE" | cut -d'=' -f2-)
    EXISTING_CHAT=$(grep -E "^CHAT_ID=" "$ENV_SOURCE" | cut -d'=' -f2-)
    EXISTING_DB_PASS=$(grep -E "^DB_PASSWORD=" "$ENV_SOURCE" | cut -d'=' -f2-)
fi

# Bot Settings
read -p "🤖 Telegram Bot Token [${EXISTING_TOKEN:-None}]: " BOT_TOKEN
BOT_TOKEN="${BOT_TOKEN:-$EXISTING_TOKEN}"

read -p "👤 Telegram Allowed Chat ID [${EXISTING_CHAT:-None}]: " CHAT_ID
CHAT_ID="${CHAT_ID:-$EXISTING_CHAT}"

# Database Password
if [ -z "$EXISTING_DB_PASS" ]; then
    DEFAULT_DB_PASS=$(openssl rand -hex 12 2>/dev/null || echo "vailib_db_pass_123")
else
    DEFAULT_DB_PASS="$EXISTING_DB_PASS"
fi
read -p "🔑 Database password [$DEFAULT_DB_PASS]: " DB_PASSWORD
DB_PASSWORD="${DB_PASSWORD:-$DEFAULT_DB_PASS}"

# 3. Clone Repository
if [ ! -d "$REPO_PATH/.git" ]; then
    echo -e "\n${CYAN}📦 Cloning Vailib repository into $REPO_PATH...${NC}"
    $SUDO mkdir -p "$REPO_PATH"
    $SUDO chown -R $(whoami):$(whoami) "$REPO_PATH"
    git clone https://github.com/vikgr/vailib.git "$REPO_PATH"
else
    echo -e "\n${CYAN}📦 Updating existing Vailib repository at $REPO_PATH...${NC}"
    cd "$REPO_PATH"
    GIT_TERMINAL_PROMPT=0 git pull origin main || echo -e "${YELLOW}⚠️ Git pull failed (credential prompt disabled). Using current repository files.${NC}"
fi

# 4. Generate Environment files
echo -e "\n${CYAN}📋 Creating environment files...${NC}"
cat <<EOF > "$REPO_PATH/.env"
POSTGRES_USER=sopds
POSTGRES_DB=sopds
DB_PASSWORD=$DB_PASSWORD
TIME_ZONE=Europe/Madrid
BOOKS_PATH=$BOOKS_PATH
DB_DATA_PATH=$COMPOSE_PATH/postgres
SOPDS_DATA_PATH=$COMPOSE_PATH/db
BOT_TOKEN=$BOT_TOKEN
CHAT_ID=$CHAT_ID
EOF

# Ensure directories exist
echo -e "\n${CYAN}📁 Creating host mount directories...${NC}"
$SUDO mkdir -p "$BOOKS_PATH" "$COMPOSE_PATH" "$COMPOSE_PATH/postgres" "$COMPOSE_PATH/db"
$SUDO chown -R $(whoami):$(whoami) "$REPO_PATH" "$BOOKS_PATH" "$COMPOSE_PATH"
touch "$BOOKS_PATH/.trigger_scan" || true

# 5. Build and Deploy
echo -e "\n${CYAN}🚀 Launching Docker stack...${NC}"
chmod +x "$REPO_PATH/deploy.sh"
cd "$REPO_PATH"
env VAILIB_DIR="$REPO_PATH" COMPOSE_FILE="$COMPOSE_PATH/docker-compose.yml" bash "$REPO_PATH/deploy.sh"

echo -e "\n${GREEN}========================================================${NC}"
echo -e "${GREEN}🎉 INSTALLATION SUCCESSFUL!${NC}"
echo -e "${GREEN}========================================================${NC}"
echo -e "Web interface:  ${YELLOW}http://${SYS_IP}:8081/web/${NC}"
echo -e "Setup Wizard:   ${YELLOW}http://${SYS_IP}:8081/web/setup/${NC}"
echo -e "Telegram Bot:   ${YELLOW}@${NC} (configured via token)"
echo -e "\n${CYAN}👉 Please open http://${SYS_IP}:8081/web/setup/ in your browser to complete setup!${NC}\n"
