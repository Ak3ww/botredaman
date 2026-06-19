import re
with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()
    chunks = re.findall(r'\"js/([^\"]+\.js)\"', text)
    print("Found chunks in app.js:", chunks[:20])

with open('chunk-vendors.dae54685.js', 'r', encoding='utf-8') as f:
    text = f.read()
    chunks2 = re.findall(r'\"js/([^\"]+\.js)\"', text)
    print("Found chunks in chunk-vendors.js:", chunks2[:20])
