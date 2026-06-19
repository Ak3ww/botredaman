with open(r'C:\BotRedaman\backend\server.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "app.post" in line or "app.put" in line:
        print(f"Line {idx+1}: {line.strip()}")
