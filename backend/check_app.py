import urllib.request
import re

req = urllib.request.Request('http://103.157.79.178:8002/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
scripts = re.findall(r'src=[\"\'](/js/[^\'\"]+)[\"\']', html)
for s in scripts:
    req_js = urllib.request.Request('http://103.157.79.178:8002' + s, headers={'User-Agent': 'Mozilla/5.0'})
    js = urllib.request.urlopen(req_js, timeout=10).read().decode('utf-8')
    if 'Vue.prototype.$getData' in js or 'Vue.prototype.$setData' in js or 'axios.post' in js or 'axios.get' in js:
        print(f'Found API logic in {s}')
        # print 200 chars around axios.post
        for match in re.finditer(r'axios\.post\s*\(\s*[\"\']?([^\s,]+)', js):
            idx = match.start()
            print(js[max(0, idx-100):min(len(js), idx+100)])

