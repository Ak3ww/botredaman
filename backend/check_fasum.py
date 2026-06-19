import sys
sys.path.insert(0, r'C:\BotRedaman\backend')
from mikrotik_client import get_mikrotik_data

_, _, secrets = get_mikrotik_data()

print("Searching Mikrotik comments for 'FASUM':")
for comment, name in secrets.items():
    if 'FASUM' in comment.upper():
        print(f"  '{comment}' -> '{name}'")
