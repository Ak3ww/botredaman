import urllib.request
import re

html = urllib.request.urlopen('http://103.157.79.178:8002/').read().decode('utf-8')
scripts = re.findall(r'src=[\"\'](/js/[^\'\"]+)[\"\']', html)
for s in scripts:
    js = urllib.request.urlopen('http://103.157.79.178:8002' + s).read().decode('utf-8')
    modules = re.findall(r'[\"\']([a-zA-Z0-9]+Info)[\"\']', js)
    modules += re.findall(r'[\"\']([a-zA-Z0-9]+List)[\"\']', js)
    modules += re.findall(r'[\"\']([a-zA-Z0-9]+Status)[\"\']', js)
    modules += re.findall(r'[\"\']([a-zA-Z0-9]+Data)[\"\']', js)
    if modules:
        print(s, set(modules))
