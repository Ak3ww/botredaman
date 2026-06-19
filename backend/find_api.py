import urllib.request
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
req = urllib.request.Request('http://103.157.79.178:8002/js/login.99675506.js', headers={'User-Agent': 'Mozilla/5.0'})
res = urllib.request.urlopen(req, timeout=10)
js = res.read().decode('utf-8')

# Find anything that looks like an endpoint path
paths = set(re.findall(r'\"(/[\w\-/\.]+)\"', js) + re.findall(r"\'(/[\w\-/\.]+)\'", js))
api = [p for p in paths if 'login' in p or 'api' in p or 'boaform' in p]
print('Paths found:', api)
