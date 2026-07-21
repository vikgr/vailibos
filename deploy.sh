#!/bin/bash
# ╔══════════════════════════════════════════════════════╗
# ║  VAILIB DEPLOY SCRIPT                               ║
# ║  Usage: bash /opt/vailib/deploy.sh                  ║
# ║  Run on: your_production_server                     ║
# ╚══════════════════════════════════════════════════════╝
set -e
VAILIB="${VAILIB_DIR:-/opt/vailib}"
COMPOSE="${COMPOSE_FILE:-/opt/sopds/docker-compose.yml}"

echo '🔄 Skipping GitHub pull (using direct push)...'
cd $VAILIB
# git pull origin main

echo '⚙️  Regenerating middleware.py...'
python3 $VAILIB/write_middleware.py

echo '⚙️  Patching settings.py (language choices)...'
python3 $VAILIB/patch_settings.py

echo '🐳 Building vailib:latest native container...'
sudo docker build -t vailib:latest -f Dockerfile_vailib .

echo '📋 Deploying docker-compose and environment variables to production...'
sudo cp $VAILIB/sopds-docker-compose.yml $COMPOSE
[ -f "$VAILIB/.env" ] && sudo cp "$VAILIB/.env" "$(dirname "$COMPOSE")/.env"

echo '🔁 Recreating and starting vailib container...'
cd "$(dirname "$COMPOSE")"
sudo docker compose up -d

echo ''
echo '✅ Deploy complete! Check your local instance!'
