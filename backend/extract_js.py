import urllib.request
import re

req = urllib.request.Request('http://103.157.79.178:8002/js/login.99675506.js', headers={'User-Agent': 'Mozilla/5.0'})
res = urllib.request.urlopen(req, timeout=10)
js = res.read().decode('utf-8')

print("=== LOGIN STRINGS ===")
for s in set(re.findall(r'[\"\']([^\'\"]*login[^\'\"]*)[\"\']', js)):
    print(s)
    
print("\n=== BOA/API/FORM STRINGS ===")
for s in set(re.findall(r'[\"\']([a-zA-Z0-9_\-/\.]*api[a-zA-Z0-9_\-/\.]*)[\"\']', js)):
    print(s)
for s in set(re.findall(r'[\"\']([a-zA-Z0-9_\-/\.]*boa[a-zA-Z0-9_\-/\.]*)[\"\']', js)):
    print(s)
for s in set(re.findall(r'[\"\']([a-zA-Z0-9_\-/\.]*form[a-zA-Z0-9_\-/\.]*)[\"\']', js)):
    print(s)
    
