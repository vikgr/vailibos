import os
import re

TEMPLATES_DIR = '/home/vik/vailib/templates'
CYRILLIC_PATTERN = re.compile(r'[\u0400-\u04FF]+')

def scan_templates():
    report = []
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if not file.endswith('.html'):
                continue
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, TEMPLATES_DIR)
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lines = content.splitlines()
            for idx, line in enumerate(lines, 1):
                # Find all Cyrillic words in the line
                matches = CYRILLIC_PATTERN.findall(line)
                if matches:
                    line_strip = line.strip()
                    # Ignore lines that are comments or within Javascript dict
                    if 'vailibDict' in line or 'dict[' in line or 'const dict' in line or 'vailibDict =' in line:
                        continue
                    if 'var vailibDict =' in line or "'ru': {" in line:
                        continue
                    if '<!--' in line and '-->' in line:
                        continue
                    if '{# ' in line and ' #}' in line:
                        continue
                    
                    has_trans_tag = '{% trans' in line or '{% blocktrans' in line
                    has_data_trans = 'data-trans=' in line
                    
                    if not (has_trans_tag or has_data_trans):
                        report.append({
                            'file': relpath,
                            'line_num': idx,
                            'line_content': line_strip,
                            'cyrillic_words': matches
                        })
    return report

results = scan_templates()
print(f'Found {len(results)} untranslated or partially untranslated items:\n')
current_file = ''
for r in results:
    if r['file'] != current_file:
        current_file = r['file']
        print(f'\n📁 File: {current_file}')
        print('-' * 50)
    print(f'  Line {r["line_num"]}: {r["line_content"]}')
    print(f'    Cyrillic detected: {r["cyrillic_words"]}')
