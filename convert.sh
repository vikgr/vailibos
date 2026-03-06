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

# The single file requested by the user
TEST_FILE="Ching Francis D. K. - Architecture. Form, Space, and Order. Fifth Edition - 2023"
PDF_FILE="${TEST_FILE}.pdf"
FB2_FILE="${TEST_FILE}.fb2"

cd /library || exit 1

echo "CONVERTER TEST MODE ACTIVE (v12)"
send_tg "🧪 Testing specific book conversion (Fixed Path): ${PDF_FILE}"

if [ ! -f "${PDF_FILE}" ]; then
    send_tg "❌ Error: File not found in /library!"
    exit 1
fi

set_status "🔄 <b>Test Conversion (Fixed)</b>
📄 File: ${PDF_FILE}
🕒 Started: $(date '+%H:%M:%S')"

# Running from within /library to avoid path creation errors
if ebook-convert "${PDF_FILE}" "${FB2_FILE}" > /tmp/converter.log 2>&1; then
    send_tg "✅ Test conversion SUCCESSFUL: ${PDF_FILE}\n\nResult: .fb2 file created."
    set_status "✅ <b>Test Complete</b>
📄 ${PDF_FILE} -> SUCCESS"
else
    LOG_TAIL=$(tail -n 15 /tmp/converter.log)
    send_tg "❌ Test conversion FAILED: ${PDF_FILE}\n\nLog tail:\n$LOG_TAIL"
    set_status "❌ <b>Test Failed</b>
📄 ${PDF_FILE} -> FAILED"
fi

echo "Test finished. Keeping container alive..."
while true; do sleep 3600; done
