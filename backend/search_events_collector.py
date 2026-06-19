with open(r'C:\BotRedaman\backend\collector.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "connection_events" in line or "DISCONNECT" in line:
        print(f"Line {idx+1}: {line.strip()}")
