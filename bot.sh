#!/bin/bash
# ============================================================
#  Unified Library Bot — Premium Experience (v12 - RELIABLE)
# ============================================================

BOT_TOKEN="${BOT_TOKEN:-7602944873:AAHJMk3UZvNSQCvID4EvmJsP68e4TYGLOZ8}"
ALLOWED_CHAT="${CHAT_ID:-1655536}"
STATUS_FILE="/tmp/convert_status.txt"
SCAN_TRIGGER="/tmp/trigger_scan"
LOG_FILE="/tmp/bot.log"
OFFSET_FILE="/tmp/bot_offset"
[ -f "$OFFSET_FILE" ] || echo "0" > "$OFFSET_FILE"

# DB Connection
DB_HOST="${DB_HOST:-db}"
DB_USER="sopds"
DB_NAME="sopds"
export PGPASSWORD="151104"

# ── Helpers ─────────────────────────────────────────────────

api() {
    curl -s "https://api.telegram.org/bot${BOT_TOKEN}/$1" "${@:2}"
}

send_msg() {
    local chat="$1"; local text="$2"; local kb="$3"
    echo "Sending MSG to $chat" >> "$LOG_FILE"
    local params=(-d chat_id="$chat" -d parse_mode="HTML" --data-urlencode "text=$text")
    [ -n "$kb" ] && params+=(-d reply_markup="$kb")
    api sendMessage "${params[@]}" >> "$LOG_FILE" 2>&1
}

edit_msg() {
    local chat="$1"; local msg_id="$2"; local text="$3"; local kb="$4"
    echo "Editing MSG $msg_id in $chat" >> "$LOG_FILE"
    local params=(-d chat_id="$chat" -d message_id="$msg_id" -d parse_mode="HTML" --data-urlencode "text=$text")
    [ -n "$kb" ] && params+=(-d reply_markup="$kb")
    api editMessageText "${params[@]}" >> "$LOG_FILE" 2>&1
}

send_photo() {
    local chat="$1"; local photo="$2"; local caption="$3"; local kb="$4"
    echo "Sending PHOTO to $chat" >> "$LOG_FILE"
    local params=(-F chat_id="$chat" -F photo="@$photo" -F caption="$caption" -F parse_mode="HTML")
    [ -n "$kb" ] && params+=(-F reply_markup="$kb")
    api sendPhoto "${params[@]}" >> "$LOG_FILE" 2>&1
}

# ── Keyboards ───────────────────────────────────────────────

kb_main() {
    echo '{"inline_keyboard": [[
        {"text": "👤 Authors", "callback_data": "browse_authors"},
        {"text": "📖 Titles", "callback_data": "browse_titles"}
    ],[
        {"text": "📊 Stats", "callback_data": "stats_db"},
        {"text": "🖥 Health", "callback_data": "status_cmd"}
    ],[
        {"text": "🔄 Scan Library", "callback_data": "scan_cmd"}
    ]]}'
}

# $1: callback_prefix (e.g. abc_auth_)
kb_letter_grid() {
    local prefix="$1"
    python3 -c "
import json
en = 'ABCDEFGHIJKLMNPQRSTUVWXYZ'
ru = 'АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЭЮЯ'
rows = []
cur = []
for l in list(en + ru):
    cur.append({'text': l, 'callback_data': '${prefix}' + l})
    if len(cur) == 6:
        rows.append(cur)
        cur = []
if cur: rows.append(cur)
rows.append([{'text': '⬅️ Back', 'callback_data': 'main_menu'}])
print(json.dumps({'inline_keyboard': rows}))
"
}

# ── Stats & Health ──────────────────────────────────────────

get_system_stats() {
    local s_up; s_up=$(curl -sf --max-time 1 "http://sopds:8001/" > /dev/null 2>&1 && echo "✅ Up" || echo "⚠️ Unreached")
    local conv_p; conv_p=$(pgrep -f convert.sh | head -1)
    local conv_v=$([ -n "$conv_p" ] && echo "✅ Running" || echo "❌ Stopped")
    local disk; disk=$(du -sh /library | awk '{print $1}')
    echo "🖥 <b>System Health</b>
📦 <b>SOPDS:</b> $s_up
🔄 <b>Converter:</b> $conv_v
💾 <b>Storage:</b> $disk"
}

get_db_stats() {
    local b_c=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -A -c "SELECT count(*) FROM opds_catalog_book")
    local a_c=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -A -c "SELECT count(*) FROM opds_catalog_author")
    local lng=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -A -c "SELECT COALESCE(NULLIF(lang, ''), 'Other') || ': ' || count(*) FROM opds_catalog_book GROUP BY 1 ORDER BY count(*) DESC LIMIT 5")
    echo "📊 <b>Library Stats</b>
📚 Books: $b_c
👤 Authors: $a_c

🌍 <b>Top Languages:</b>
$lng"
}

# ── List Builder ────────────────────────────────────────────

build_kb() {
    local back_cb="$1"
    python3 -c "
import sys, json
kb = []
for line in sys.stdin:
    if '|' in line:
        try:
            txt, data = line.strip().split('|', 1)
            kb.append([{'text': txt, 'callback_data': data}])
        except: continue
kb.append([{'text': '⬅️ Back', 'callback_data': '$back_cb'}])
print(json.dumps({'inline_keyboard': kb}))
"
}

# ── Handlers ────────────────────────────────────────────────

handle_authors_letter() {
    local chat="$1"; local msg_id="$2"; local L="$3"
    echo "Fetching authors for $L" >> "$LOG_FILE"
    local kb; kb=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -A -t -c "SELECT full_name || '|auth_' || id FROM opds_catalog_author WHERE full_name ILIKE '${L}%' ORDER BY full_name LIMIT 15" | build_kb "browse_authors")
    edit_msg "$chat" "$msg_id" "👤 Authors (<b>$L</b>):" "$kb"
}

handle_titles_letter() {
    local chat="$1"; local msg_id="$2"; local L="$3"
    echo "Fetching titles for $L" >> "$LOG_FILE"
    local kb; kb=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -A -t -c "SELECT left(title, 40) || '|bk_' || id FROM opds_catalog_book WHERE title ILIKE '${L}%' ORDER BY title LIMIT 15" | build_kb "browse_titles")
    edit_msg "$chat" "$msg_id" "📖 Titles (<b>$L</b>):" "$kb"
}

handle_author_detail() {
    local chat="$1"; local msg_id="$2"; local aid="$3"
    local name; name=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -A -c "SELECT full_name FROM opds_catalog_author WHERE id = $aid")
    local kb; kb=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -A -t -c "SELECT left(b.title, 40) || '|bk_' || b.id FROM opds_catalog_book b JOIN opds_catalog_bauthor ba ON b.id = ba.book_id WHERE ba.author_id = ${aid} LIMIT 15" | build_kb "browse_authors")
    edit_msg "$chat" "$msg_id" "📚 Books by <b>$name</b>:" "$kb"
}

handle_book_detail() {
    local chat="$1"; local id="$2"
    local data=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -A -t -F "|" -c "SELECT title, path, filename, format, lang FROM opds_catalog_book WHERE id = $id")
    IFS='|' read -r title p_val f_val fmt lng <<< "$data"
    
    local txt="📖 <b>$title</b>\n🌍 Language: $lng\n📄 Format: $fmt"
    local kb='{"inline_keyboard": [[{"text": "📥 Download", "callback_data": "dl_'${id}'"}],[{"text": "⬅️ Back", "callback_data": "main_menu"}]]}'
    
    local f_path="/library/${p_val}/${f_val}"
    local cov="/tmp/cov_${id}.jpg"
    
    # Only try cover extraction if load is low. 
    local load=$(awk '{print $1}' /proc/loadavg | cut -f1 -d'.')
    if [ "$load" -lt 10 ]; then
        rm -f "$cov"
        ebook-meta "$f_path" --get-cover="$cov" >/dev/null 2>&1
        if [ -f "$cov" ]; then
            send_photo "$chat" "$cov" "$txt" "$kb"
            rm -f "$cov"
            return
        fi
    fi
    send_msg "$chat" "$txt" "$kb"
}

handle_search() {
    local chat="$1"; local q="$2"
    local kb; kb=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -A -t -c "
        SELECT left(title, 40) || '|bk_' || id FROM (
            SELECT id, title FROM opds_catalog_book WHERE title ILIKE '%$q%' 
            UNION 
            SELECT b.id, b.title FROM opds_catalog_book b JOIN opds_catalog_bauthor ba ON b.id = ba.book_id JOIN opds_catalog_author a ON ba.author_id = a.id WHERE a.full_name ILIKE '%$q%'
            LIMIT 15
        ) t" | build_kb "main_menu")
    send_msg "$chat" "🔎 Results for <b>$q</b>:" "$kb"
}

# ── Update Processer ─────────────────────────────────────────

process_update() {
    local chat_id="$1"; local payload="$2"; local msg_id="$3"; local cb_id="$4"
    echo "Processing update: $payload (chat $chat_id)" >> "$LOG_FILE"
    
    if [ -z "$cb_id" ]; then
        # Message handling
        case "$payload" in
            /start*) send_msg "$chat_id" "📚 <b>HProliant Dashboard</b>" "$(kb_main)" ;;
            /status*) send_msg "$chat_id" "$(get_system_stats)" ;;
            /stats*)  send_msg "$chat_id" "$(get_db_stats)" ;;
            *)        handle_search "$chat_id" "$payload" ;;
        esac
    else
        # Callback query
        api answerCallbackQuery -d callback_query_id="$cb_id" >/dev/null 2>&1
        case "$payload" in
            main_menu)      edit_msg "$chat_id" "$msg_id" "📚 <b>HProliant Dashboard</b>" "$(kb_main)" ;;
            stats_db)       edit_msg "$chat_id" "$msg_id" "$(get_db_stats)" "$(kb_main)" ;;
            status_cmd)     edit_msg "$chat_id" "$msg_id" "$(get_system_stats)" "$(kb_main)" ;;
            browse_authors) edit_msg "$chat_id" "$msg_id" "👤 Select author letter:" "$(kb_letter_grid 'abc_auth_')" ;;
            browse_titles)  edit_msg "$chat_id" "$msg_id" "📖 Select title letter:" "$(kb_letter_grid 'abc_title_')" ;;
            abc_auth_*)     handle_authors_letter "$chat_id" "$msg_id" "${payload#abc_auth_}" ;;
            abc_title_*)    handle_titles_letter  "$chat_id" "$msg_id" "${payload#abc_title_}" ;;
            auth_*)         handle_author_detail  "$chat_id" "$msg_id" "${payload#auth_}" ;;
            bk_*)           handle_book_detail    "$chat_id" "${payload#bk_}" ;;
            scan_cmd)       touch "$SCAN_TRIGGER"; edit_msg "$chat_id" "$msg_id" "🔎 <b>Library scan triggered\!</b>" "$(kb_main)" ;;
            dl_*)           
                local d; d=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -A -t -F "|" -c "SELECT path, filename FROM opds_catalog_book WHERE id = ${payload#dl_}")
                IFS='|' read -r pv fv <<< "$d"
                api sendDocument -F chat_id="$chat_id" -F document="@/library/${pv}/${fv}" >/dev/null 2>&1
            ;;
        esac
    fi
}

# ── Main Loop ───────────────────────────────────────────────

api deleteWebhook >/dev/null
echo "Bot (v12) started at $(date)" >> "$LOG_FILE"

while true; do
    offset=$(cat "$OFFSET_FILE")
    response=$(api getUpdates -d offset="$offset" -d timeout=20 -d allowed_updates='["message","callback_query"]')
    
    # Parse into pipe-separated: type|up_id|chat_id|payload|msg_id|cb_id
    echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('ok'):
        for u in data.get('result', []):
            up_id = u['update_id']
            if 'callback_query' in u:
                cb = u['callback_query']
                print(f'CB|{up_id}|{cb[\"message\"][\"chat\"][\"id\"]}|{cb.get(\"data\",\"\")}|{cb[\"message\"][\"message_id\"]}|{cb[\"id\"]}')
            elif 'message' in u:
                m = u['message']
                print(f'MSG|{up_id}|{m[\"chat\"][\"id\"]}|{m.get(\"text\",\"\")}||')
except: pass
" 2>/dev/null | while IFS='|' read -r type up_id chat_id payload msg_id cb_id; do
        [ -z "$up_id" ] && continue
        
        # Save exact offset
        echo $((up_id + 1)) > "$OFFSET_FILE"
        [ "$chat_id" != "$ALLOWED_CHAT" ] && continue
        
        # Dispatch in background for speed
        if [ "$type" == "CB" ]; then
            process_update "$chat_id" "$payload" "$msg_id" "$cb_id" &
        else
            process_update "$chat_id" "$payload" "" "" &
        fi
    done
    sleep 0.2
done
