#######################################################################
#
# Вспомогательные функции
#
import unicodedata
import re

def translit(s):
    """Translit: converts Cyrillic to Latin, and now handles some Greek-like characters too."""
    if not isinstance(s, str):
        return str(s)

    # Cyrillic tables
    table1 = str.maketrans("абвгдеёзийклмнопрстуфхъыьэАБВГДЕЁЗИЙКЛМНОПРСТУФХЪЫЬЭ",  "abvgdeezijklmnoprstufh'y'eABVGDEEZIJKLMNOPRSTUFH'Y'E")
    table2 = {'ж':'zh','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ю':'ju','я':'ja',  'Ж':'Zh','Ц':'Ts','Ч':'Ch','Ш':'Sh','Щ':'Sch','Ю':'Ju','Я':'Ja', 
              '«':'', '»':'','"':'','\n':'_',' ':'_',"'":"",':':'_','№':'N'}
              
    # Add some Greek support if it looks like Greek but should be Latin (common for some old encodings or scannings)
    # Γ -> G, Δ -> D, Λ -> L, Π -> P, Σ -> S, Φ -> Ph, Ψ -> Ps, Ω -> O
    greek_table = {
        'Γ':'G', 'Δ':'D', 'Θ':'Th', 'Λ':'L', 'Ξ':'X', 'Π':'P', 'Σ':'S', 'Φ':'Ph', 'Ψ':'Ps', 'Ω':'O',
        'γ':'g', 'δ':'d', 'θ':'th', 'λ':'l', 'ξ':'x', 'π':'p', 'σ':'s', 'φ':'ph', 'ψ':'ps', 'ω':'o'
    }
    
    s = s.translate(table1)
    for k, v in table2.items():
        s = s.replace(k, v)
    for k, v in greek_table.items():
        s = s.replace(k, v)
        
    return s

def to_ascii(s):
    """Normalize to ASCII, but be smarter than just replacing with '?'."""
    # First, try to decompose and strip accents
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', 'ignore').decode('utf-8')
    # If it's now too short or empty, it means we lost too much.
    # But for filenames it's better than question marks.
    return s

def to_human_filename(name):
    """Clean up filename to be safe but readable."""
    # Replace non-word chars with underscores or spaces
    name = re.sub(r'[^\w\s\.\-\(\),]', '_', name)
    # Replace multiple underscores/spaces
    name = re.sub(r'[\s_]+', '_', name)
    return name.strip('_')
