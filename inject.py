import re

with open("docker/src/vailib_web_backend/templates/vailib_main.html", "r", encoding="utf-8") as f:
    text = f.read()

# find vailibDict
match = re.search(r"(const vailibDict = \{.*?\n        \};\n\n        function setVailibLang.*?document\.addEventListener\(\"DOMContentLoaded\", applyVailibLang\);)", text, re.DOTALL)
if match:
    js_code = match.group(1)
    
    with open("templates/sopds_main.html", "r", encoding="utf-8") as f2:
        main_html = f2.read()
        
    # Inject JS
    main_html = main_html.replace("$(document).foundation();", js_code + "\n\n        $(document).foundation();")
    
    # Inject HTML
    lang_html = """
                <div class="lang-selector-container" style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; background: transparent; border: none; box-shadow: none; padding: 0; margin: 15px 0 0 0;">
                    <a href="#" onclick="setVailibLang('ru'); return false;" class="color-lang-btn" style="padding: 4px 2px; justify-content: center; gap: 3px;"><img src="https://flagcdn.com/w20/ru.png" width="15" alt="RU" style="border-radius:2px;"> <span class="lang-code" style="font-size:0.75rem; font-weight:800;">RU</span></a>
                    <a href="#" onclick="setVailibLang('en'); return false;" class="color-lang-btn" style="padding: 4px 2px; justify-content: center; gap: 3px;"><img src="https://flagcdn.com/w20/gb.png" width="15" alt="EN" style="border-radius:2px;"> <span class="lang-code" style="font-size:0.75rem; font-weight:800;">EN</span></a>
                    <a href="#" onclick="setVailibLang('de'); return false;" class="color-lang-btn" style="padding: 4px 2px; justify-content: center; gap: 3px;"><img src="https://flagcdn.com/w20/de.png" width="15" alt="DE" style="border-radius:2px;"> <span class="lang-code" style="font-size:0.75rem; font-weight:800;">DE</span></a>
                    <a href="#" onclick="setVailibLang('es'); return false;" class="color-lang-btn" style="padding: 4px 2px; justify-content: center; gap: 3px;"><img src="https://flagcdn.com/w20/es.png" width="15" alt="ES" style="border-radius:2px;"> <span class="lang-code" style="font-size:0.75rem; font-weight:800;">ES</span></a>
                    <a href="#" onclick="setVailibLang('fr'); return false;" class="color-lang-btn" style="padding: 4px 2px; justify-content: center; gap: 3px;"><img src="https://flagcdn.com/w20/fr.png" width="15" alt="FR" style="border-radius:2px;"> <span class="lang-code" style="font-size:0.75rem; font-weight:800;">FR</span></a>
                    <a href="#" onclick="setVailibLang('el'); return false;" class="color-lang-btn" style="padding: 4px 2px; justify-content: center; gap: 3px;"><img src="https://flagcdn.com/w20/gr.png" width="15" alt="GR" style="border-radius:2px;"> <span class="lang-code" style="font-size:0.75rem; font-weight:800;">GR</span></a>
                    <a href="#" onclick="setVailibLang('ar'); return false;" class="color-lang-btn" style="padding: 4px 2px; justify-content: center; gap: 3px;"><img src="https://flagcdn.com/w20/sa.png" width="15" alt="AR" style="border-radius:2px;"> <span class="lang-code" style="font-size:0.75rem; font-weight:800;">AR</span></a>
                    <a href="#" onclick="setVailibLang('hi'); return false;" class="color-lang-btn" style="padding: 4px 2px; justify-content: center; gap: 3px;"><img src="https://flagcdn.com/w20/in.png" width="15" alt="HI" style="border-radius:2px;"> <span class="lang-code" style="font-size:0.75rem; font-weight:800;">HI</span></a>
                    <a href="#" onclick="setVailibLang('pt'); return false;" class="color-lang-btn" style="padding: 4px 2px; justify-content: center; gap: 3px;"><img src="https://flagcdn.com/w20/pt.png" width="15" alt="PT" style="border-radius:2px;"> <span class="lang-code" style="font-size:0.75rem; font-weight:800;">PT</span></a>
                    <a href="#" onclick="setVailibLang('zh'); return false;" class="color-lang-btn" style="padding: 4px 2px; justify-content: center; gap: 3px;"><img src="https://flagcdn.com/w20/cn.png" width="15" alt="ZH" style="border-radius:2px;"> <span class="lang-code" style="font-size:0.75rem; font-weight:800;">ZH</span></a>
                </div>
"""
    main_html = main_html.replace('<h1 class="vailib-brand" style="margin:0;">VAILIB</h1>\n                </a>', '<h1 class="vailib-brand" style="margin:0;">VAILIB</h1>\n                </a>\n' + lang_html)
    
    with open("templates/sopds_main.html", "w", encoding="utf-8") as f3:
        f3.write(main_html)
    print("Injected successfully.")
else:
    print("Could not find regex.")
