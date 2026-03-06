#!/bin/bash
BOT_TOKEN="${BOT_TOKEN:-7602944873:AAHJMk3UZvNSQCvID4EvmJsP68e4TYGLOZ8}"
CHAT_ID="${CHAT_ID:-1655536}"

send_tg() {
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d chat_id="${CHAT_ID}" \
        -d text="$1" > /dev/null
}

FILE="/books/Ching Francis D. K. - Architecture. Form, Space, and Order. Fifth Edition - 2023.pdf"
TARGET="${FILE%.*}.fb2"

send_tg "🧪 Testing conversion for: $FILE"
echo "Starting test conversion..."

if ebook-convert "$FILE" "$TARGET" > /tmp/test_convert.log 2>&1; then
    send_tg "✅ Test conversion SUCCESSFUL: $(basename "$FILE")"
    echo "Success!"
else
    send_tg "❌ Test conversion FAILED: $(basename "$FILE")"
    echo "Failed. Check /tmp/test_convert.log inside container."
fi
