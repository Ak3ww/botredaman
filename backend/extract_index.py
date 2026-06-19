import sys, requests, hashlib, json, re
url = 'http://192.168.30.3:8001'
m = hashlib.md5()
m.update(('an3400' + '#eugine0909').encode('utf-8'))
headers = {'Referer': f'{url}/login.html', 'Connection': 'close', 'User-Agent': 'Mozilla/5.0'}
r = requests.post(f'{url}/setModules', headers=headers, json={'login': {'username': 'root', 'password': m.hexdigest()}}, timeout=10)
cookies = r.cookies.get_dict()
headers['token'] = r.headers.get('token', '')

idx = requests.get(f'{url}/index.html', headers=headers, cookies=cookies)
print('JS files in index.html:')
js_files = re.findall(r'src=\"([^\"]+\.js)\"', idx.text)
print(js_files)

all_info = set()
for jf in js_files:
    if not jf.startswith('/'):
        jf = '/' + jf
    try:
        r2 = requests.get(url + jf, timeout=5)
        modules = re.findall(r'"([a-zA-Z]+Info)"', r2.text)
        all_info.update(modules)
        modules2 = re.findall(r'\"([a-zA-Z]*ont[a-zA-Z]*)\"', r2.text)
        all_info.update(modules2)
    except Exception as e:
        pass
print('Found modules:')
print(json.dumps(list(all_info), indent=2))
