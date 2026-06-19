import requests, re
try:
    r = requests.get("http://192.168.30.3:8001/login.html", timeout=5)
    print("JS files in login.html:")
    print(re.findall(r'src=\"([^\"]+\.js)\"', r.text))
except Exception as e:
    print(e)
