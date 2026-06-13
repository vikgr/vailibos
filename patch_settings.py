with open('/tmp/sopds_custom/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """        'choices': (("ru-RU", "Russian"), ("en-US", "English"))"""
new = """        'choices': (
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

if old in content:
    content = content.replace(old, new)
    with open('/tmp/sopds_custom/settings.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK: choices expanded to 11 languages")
else:
    print("WARNING: pattern not found, checking file...")
    for i, line in enumerate(content.splitlines(), 1):
        if 'choices' in line:
            print(f"  Line {i}: {repr(line)}")

# Register Setup Middleware in settings.py MIDDLEWARE list
with open('/tmp/sopds_custom/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

setup_middleware = "'opds_catalog.middleware.SOPDSSetupMiddleware'"
if setup_middleware not in content:
    locale_middleware = "'opds_catalog.middleware.SOPDSLocaleMiddleware'"
    if locale_middleware in content:
        content = content.replace(locale_middleware, f"{setup_middleware},\n    {locale_middleware}")
        with open('/tmp/sopds_custom/settings.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("OK: SOPDSSetupMiddleware registered in settings.py")

