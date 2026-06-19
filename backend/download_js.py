import urllib.request
import re
import os

url = 'http://192.168.30.5:8002'
html = urllib.request.urlopen(f'{url}/').read().decode('utf-8')
scripts = re.findall(r'src=[\"\'](/js/[^\'\"]+)[\"\']', html)

os.makedirs('js_dump', exist_ok=True)
for s in scripts:
    js = urllib.request.urlopen(f'{url}{s}').read()
    filename = s.split('/')[-1]
    with open('js_dump/' + filename, 'wb') as f:
        f.write(js)
    print("Downloaded", filename)
