import sys
sys.path.insert(0, r'C:\BotRedaman\backend')
from mikrotik_client import get_mikrotik_data

active, queues, secrets = get_mikrotik_data()
print(f"Active users: {len(active)}")
print(f"Queues: {len(queues)}")
print(f"Secrets (with comments): {len(secrets)}")

if secrets:
    print("\n--- Sample secrets (comment -> pppoe_name) ---")
    for i, (comment, name) in enumerate(secrets.items()):
        if i >= 10:
            break
        print(f"  '{comment}' -> '{name}'")
    print("\n✅ Mikrotik connected! Secrets loaded successfully.")
else:
    print("\n❌ No secrets. Mikrotik may still be failing.")
