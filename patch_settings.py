import os
import re

settings_path = '/sopds/sopds/settings.py'
# Fallback for local workspace scripting / diagnostics
if not os.path.exists(settings_path):
    settings_path = '/tmp/sopds_custom/settings.py'
if not os.path.exists(settings_path):
    settings_path = './settings.py'

if os.path.exists(settings_path):
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    old_choices = "'choices': ((\"ru-RU\", \"Russian\"), (\"en-US\", \"English\"))"
    new_choices = """'choices': (
            ("en-us",   "English"),
            ("ru",      "Russian"),
            ("de",      "German"),
            ("el",      "Greek"),
            ("es",      "Spanish"),
            ("fr",      "French"),
            ("ar",      "Arabic"),
            ("hi",      "Hindi"),
            ("pt",      "Portuguese"),
            ("zh-hans", "Chinese"),
            ("bn",      "Bengali"),
            ("nl",      "Dutch"),
        )"""

    if old_choices in content:
        content = content.replace(old_choices, new_choices)
        print("OK: choices expanded to 12 languages")
    else:
        # Fallback to regex replacing choices block if already modified (e.g. 11 languages list)
        pattern = r"'choices':\s*\([\s\S]*?\)"
        match = re.search(pattern, content)
        if match:
            content = content.replace(match.group(0), new_choices, 1)
            print("OK: choices updated to 12 languages robustly via regex")
        else:
            print("WARNING: choices pattern block not found")

    # Register Setup Middleware in settings.py MIDDLEWARE list
    setup_middleware = "'opds_catalog.middleware.SOPDSSetupMiddleware'"
    if setup_middleware not in content:
        locale_middleware = "'opds_catalog.middleware.SOPDSLocaleMiddleware'"
        if locale_middleware in content:
            content = content.replace(locale_middleware, f"{setup_middleware},\n    {locale_middleware}")
            print("OK: SOPDSSetupMiddleware registered in settings.py")
        else:
            print("WARNING: SOPDSLocaleMiddleware not found, skipping middleware patch")
    else:
        print("INFO: SOPDSSetupMiddleware already registered")

    # Register Theme Middleware in settings.py MIDDLEWARE list
    theme_middleware = "'opds_catalog.middleware.VailibThemeMiddleware'"
    if theme_middleware not in content:
        if setup_middleware in content:
            content = content.replace(setup_middleware, f"{theme_middleware},\n    {setup_middleware}")
            print("OK: VailibThemeMiddleware registered in settings.py")
        else:
            print("WARNING: SOPDSSetupMiddleware not found in settings, skipping theme middleware registration")
    else:
        print("INFO: VailibThemeMiddleware already registered")

    # Register Telegram Bot Constance Configs in settings.py
    if "SOPDS_TELEBOT_CHAT_ID" not in content:
        telebot_pid = "('SOPDS_TELEBOT_PID', (os.path.join(BASE_DIR, 'opds_catalog/tmp/sopds_telebot.pid'), _('Path to pidfile for sopds_telebot process'))),"
        new_telebot_configs = """('SOPDS_TELEBOT_PID', (os.path.join(BASE_DIR, 'opds_catalog/tmp/sopds_telebot.pid'), _('Path to pidfile for sopds_telebot process'))),
    ('SOPDS_TELEBOT_CHAT_ID', ('', _('Allowed Telegram Chat ID for Bot Assistant'))),
    ('SOPDS_TELEBOT_ENABLED', (True, _('Enable custom Telegram Assistant Bot'))),"""
        content = content.replace(telebot_pid, new_telebot_configs)
        print("OK: Telegram bot settings registered in CONSTANCE_CONFIG")
        
        # Also register in fieldsets
        old_fieldsets = "'5. Telegramm Bot Options': ('SOPDS_TELEBOT_API_TOKEN','SOPDS_TELEBOT_AUTH','SOPDS_TELEBOT_MAXITEMS'),"
        new_fieldsets = "'5. Telegramm Bot Options': ('SOPDS_TELEBOT_API_TOKEN','SOPDS_TELEBOT_AUTH','SOPDS_TELEBOT_MAXITEMS','SOPDS_TELEBOT_CHAT_ID','SOPDS_TELEBOT_ENABLED'),"
        content = content.replace(old_fieldsets, new_fieldsets)
        print("OK: Telegram bot settings registered in CONSTANCE_CONFIG_FIELDSETS")

    # Configure upload size limits for books and archives (1GB max request, 25MB in-memory buffer)
    if "DATA_UPLOAD_MAX_MEMORY_SIZE" not in content:
        upload_limits = """
# File upload limits for books and archives
DATA_UPLOAD_MAX_MEMORY_SIZE = 1073741824  # 1 GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400   # 25 MB
"""
        content += upload_limits
        print("OK: Upload size limits configured (1GB)")

    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print(f"WARNING: settings.py not found at {settings_path}")


