#!/bin/bash
# ============================================================
#  Converter Script (v12 - RELIABLE)
# ============================================================

BOT_TOKEN="${BOT_TOKEN:-7602944873:AAHJMk3UZvNSQCvID4EvmJsP68e4TYGLOZ8}"
CHAT_ID="${CHAT_ID:-1655536}"
STATUS_FILE="/tmp/convert_status.txt"

send_tg() {
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d chat_id="${CHAT_ID}" \
        -d text="$1" > /dev/null
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
