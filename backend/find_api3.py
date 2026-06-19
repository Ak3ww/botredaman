import urllib.request
import re

url = 'http://192.168.30.5:8002'
html = urllib.request.urlopen(f'{url}/').read().decode('utf-8')
scripts = re.findall(r'src=[\"\'](/js/[^\'\"]+)[\"\']', html)
for s in scripts:
    js = urllib.request.urlopen(f'{url}{s}').read().decode('utf-8')
    keys = re.findall(r'([a-zA-Z0-9]+Info|[a-zA-Z0-9]+Status|[a-zA-Z0-9]+List|[a-zA-Z0-9]+Optical|[a-zA-Z0-9]*Onu[a-zA-Z0-9]*|[a-zA-Z0-9]*Pon[a-zA-Z0-9]*)', js)
    valid = set(k for k in keys if len(k) > 4)
    if valid:
        print('===', s, '===')
        print(sorted(valid))
