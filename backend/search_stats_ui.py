import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\BotRedaman\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "STATS" in line:
        print(f"Line {idx+1}: {line.strip()}")
