import urllib.request
import re

url = 'http://192.168.30.5:8002'
html = urllib.request.urlopen(f'{url}/').read().decode('utf-8')
scripts = re.findall(r'src=[\"\'](/js/[^\'\"]+)[\"\']', html)
for s in scripts:
    js = urllib.request.urlopen(f'{url}{s}').read().decode('utf-8')
    keys = re.findall(r'\"([a-zA-Z0-9]+)\"\s*:\s*(?:\"\"|\{\})', js)
    valid_keys = [k for k in set(keys) if 'Info' in k or 'Onu' in k or 'Status' in k or 'List' in k or 'Port' in k or 'Pon' in k]
    if valid_keys:
        print(s, valid_keys)
        
    print("ALL KEYS in", s)
    print(set(keys))
