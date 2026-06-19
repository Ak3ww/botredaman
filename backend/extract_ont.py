import requests, re, json
url = 'http://192.168.30.3:8001'
js_files = ['/js/app.js', '/js/chunk-vendors.dae54685.js', '/js/chunk-common.d515ccfe.js', '/js/login.7862118f.js']
all_ont = set()
for jf in js_files:
    try:
        r = requests.get(url + jf, timeout=5)
        # Find any string containing 'ont' that might be an endpoint
        modules = re.findall(r'"([a-zA-Z]*ont[a-zA-Z0-9]*)"', r.text)
        all_ont.update(modules)
        # Find any dictionary keys that look like 'ontName' or 'authDesc'
        keys = re.findall(r'"([a-zA-Z]*Name)"', r.text)
        all_ont.update(keys)
    except Exception as e:
        pass
print(json.dumps(list(all_ont), indent=2))
