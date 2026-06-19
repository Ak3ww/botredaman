import requests, re, json
url = 'http://192.168.30.3:8001'
js_files = ['/js/app.js', '/js/chunk-vendors.dae54685.js', '/js/chunk-common.d515ccfe.js', '/js/login.7862118f.js']
all_modules = set()
for jf in js_files:
    try:
        r = requests.get(url + jf, timeout=5)
        modules = re.findall(r'"([a-zA-Z]+Info)"', r.text)
        all_modules.update(modules)
        modules2 = re.findall(r'"(ont[a-zA-Z]+)"', r.text)
        all_modules.update(modules2)
    except Exception as e:
        print(f"Failed {jf}: {e}")

print("Found modules:")
print(json.dumps(list(all_modules), indent=2))
