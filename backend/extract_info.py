import requests, re, json
url = 'http://192.168.30.3:8001'
js_files = ['/js/app.js', '/js/chunk-vendors.dae54685.js', '/js/chunk-common.d515ccfe.js', '/js/login.7862118f.js']
all_info = set()
for jf in js_files:
    try:
        r = requests.get(url + jf, timeout=5)
        modules = re.findall(r'"([a-zA-Z]+Info)"', r.text)
        all_info.update(modules)
        # also search for 'ont' anything
        modules2 = re.findall(r'\"([a-zA-Z]*ont[a-zA-Z]*)\"', r.text)
        all_info.update(modules2)
    except Exception as e:
        pass
print(json.dumps(list(all_info), indent=2))
