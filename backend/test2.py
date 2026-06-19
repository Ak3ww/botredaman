import sys, requests, hashlib, json, time
url = 'http://192.168.30.5:8002'
m = hashlib.md5()
m.update(('an3400' + 'ggclink0lt').encode('utf-8'))
headers = {'Referer': f'{url}/login.html', 'Connection': 'close', 'User-Agent': 'Mozilla/5.0'}
r = requests.post(f'{url}/setModules', headers=headers, json={'login': {'username': 'root', 'password': m.hexdigest()}}, timeout=10)
cookies = r.cookies.get_dict()
headers['token'] = r.headers.get('token', '')

for i in range(10):
    core_payload = {'onuLightInfo': {'slotNumber': 1, 'ponPort': 0, 'pageNum': 1, 'pageCount': 500}, 'authorizedList': {'slotNumber': 1, 'ponPort': 0, 'pageNum': 1, 'pageCount': 500}}
    try:
        r_core = requests.post(f'{url}/getModules', headers=headers, cookies=cookies, json=core_payload, timeout=10)
        print(f'Attempt {i+1}: errCode=', r_core.json().get('errCode'))
    except Exception as e:
        print(f'Attempt {i+1}: Exception {e}')
    time.sleep(1)
