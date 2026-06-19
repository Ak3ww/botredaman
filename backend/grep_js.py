import os
import re

for file in os.listdir('js_dump'):
    with open('js_dump/' + file, 'r', encoding='utf-8') as f:
        js = f.read()
    
    keys = re.findall(r'\"([a-zA-Z0-9]*[Oo]nu[a-zA-Z0-9]*)\"', js)
    keys += re.findall(r'\"([a-zA-Z0-9]*[Pp]on[a-zA-Z0-9]*)\"', js)
    keys += re.findall(r'\"([a-zA-Z0-9]*[Oo]ptical[a-zA-Z0-9]*)\"', js)
    keys += re.findall(r'\"([a-zA-Z0-9]*[Ii]nfo[a-zA-Z0-9]*)\"', js)
    keys += re.findall(r'\"([a-zA-Z0-9]*[Ss]tatus[a-zA-Z0-9]*)\"', js)
    print(file, '->', set([k for k in keys if len(k)>3]))
