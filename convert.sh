#!/bin/bash
# ============================================================
#  Converter Script (v12 - RELIABLE)
# ============================================================

BOT_TOKEN="${BOT_TOKEN:-YOUR_TELEGRAM_BOT_TOKEN}"
CHAT_ID="${CHAT_ID:-YOUR_TELEGRAM_CHAT_ID}"
STATUS_FILE="/tmp/convert_status.txt"

check_convert_config() {
    local out
    out=$(python3 -c "
import sys, os
sys.path.insert(0, '/sopds')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sopds.settings')
import django
django.setup()
from constance import config
t = getattr(config, 'SOPDS_TELEBOT_API_TOKEN', '')
c = getattr(config, 'SOPDS_TELEBOT_CHAT_ID', '')
print(f'{t}|{c}')
" 2>/dev/null | tail -n 1 | tr -d '\r\n')

    if [ -n "$out" ] && [[ "$out" == *"|"* ]]; then
        IFS='|' read -r DB_TOKEN DB_CHAT <<< "$out"
        [ -n "$DB_TOKEN" ] && [ "$DB_TOKEN" != "None" ] && [ "$DB_TOKEN" != "YOUR_TELEGRAM_BOT_TOKEN" ] && BOT_TOKEN="$DB_TOKEN"
        [ -n "$DB_CHAT" ] && [ "$DB_CHAT" != "None" ] && CHAT_ID="$DB_CHAT"
    fi
}

check_convert_config

send_tg() {
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d chat_id="${CHAT_ID}" \
        -d parse_mode="HTML" \
        --data-urlencode "text=$1" > /dev/null
}

set_status() {
    echo -e "$1" > "$STATUS_FILE"
}

# The conversion loop
QUEUE_FILE="/tmp/convert_queue"
[ -f "$QUEUE_FILE" ] || touch "$QUEUE_FILE"

echo "CONVERTER WORKER STARTED (v12)"
send_tg "🤖 <b>Converter Worker Online</b>
Watching for PDF/DjVu uploads..."

while true; do
    if [ -s "$QUEUE_FILE" ]; then
        # Take the first line
        TARGET_FILE=$(head -n 1 "$QUEUE_FILE")
        # Remove it from queue
        sed -i '1d' "$QUEUE_FILE"
        
        if [ ! -f "$TARGET_FILE" ]; then
            send_tg "⚠️ Queue error: File not found: ${TARGET_FILE}"
            continue
        fi
        
        PDF_FILE="$TARGET_FILE"
        FB2_FILE="${TARGET_FILE%.*}.fb2"
        
        echo "🔄 Converting: $PDF_FILE"
        send_tg "🔄 <b>Converting:</b> <code>$(basename "$PDF_FILE")</code>"
        set_status "🔄 <b>Processing</b>
📄 $(basename "$PDF_FILE")
🕒 Started: $(date '+%H:%M:%S')"

        if ebook-convert "$PDF_FILE" "$FB2_FILE" > /tmp/converter.log 2>&1; then
            send_tg "✅ <b>Conversion Success!</b>
📄 <code>$(basename "$FB2_FILE")</code> created.
🔎 <i>Triggering re-scan...</i>"
            set_status "✅ <b>Success</b>
📄 $(basename "$FB2_FILE")"
            touch "/library/.trigger_scan"
        else
            LOG_TAIL=$(tail -n 15 /tmp/converter.log)
            send_tg "❌ <b>Conversion Failed!</b>
📄 <code>$(basename "$PDF_FILE")</code>
Log tail:
<pre>$LOG_TAIL</pre>"
            set_status "❌ <b>Failed</b>
📄 $(basename "$PDF_FILE")"
        fi
    fi
    sleep 2
done
