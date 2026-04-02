#!/bin/bash
# ╔══════════════════════════════════════════════════════╗
# ║  VAILIB DEPLOY SCRIPT                               ║
# ║  Usage: bash /home/vik/vailib/deploy.sh             ║
# ║  Run on: hproliant (192.168.31.115)                 ║
# ╚══════════════════════════════════════════════════════╝
set -e
VAILIB=/home/vik/vailib
SOPDS_CUSTOM=/tmp/sopds_custom
COMPOSE=/DATA/AppData/sopds/docker-compose.yml

echo '🔄 Pulling latest from GitHub...'
cd $VAILIB
git pull origin main

echo '⚙️  Regenerating middleware.py...'
python3 $VAILIB/write_middleware.py

echo '⚙️  Patching settings.py (language choices)...'
python3 $VAILIB/patch_settings.py

echo '📋 Deploying docker-compose to production...'
sudo cp $VAILIB/sopds-docker-compose.yml $COMPOSE

echo '🔁 Restarting sopds container...'
sudo docker restart sopds

echo ''
echo '✅ Deploy complete! Site: http://opds.workzilla.nl/web/'
