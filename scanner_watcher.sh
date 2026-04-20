#!/bin/bash
# ============================================================
#  Scanner Watcher (v1.0)
# ============================================================
TRIGGER_FILE="/library/.trigger_scan"

echo "SCANNER WATCHER STARTED"
[ -f "$TRIGGER_FILE" ] && rm -f "$TRIGGER_FILE"

while true; do
    if [ -f "$TRIGGER_FILE" ]; then
        echo "🔎 Trigger detected! Starting scan..."
        rm -f "$TRIGGER_FILE"
        python3 /sopds/manage.py sopds_scanner scan
        echo "✅ Scan complete."
    fi
    sleep 5
done
