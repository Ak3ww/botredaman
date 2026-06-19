with open('C:/BotRedaman/backend/collector.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''    def fetch_mikrotik():
        try:
            return get_mikrotik_data()
        except Exception as e:
            print(f"  [WARN] Gagal menarik data Mikrotik: {e}")
            return [], {}, {}'''

replacement = '''    def fetch_mikrotik():
        try:
            return get_mikrotik_data()
        except Exception as e:
            print(f"  [WARN] Gagal menarik data Mikrotik: {e}")
            return [], {}, {}
            
    active_users, queues_traffic, ppp_secrets = fetch_mikrotik()'''

if target in content:
    content = content.replace(target, replacement)
    with open('C:/BotRedaman/backend/collector.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed collector.py missing ppp_secrets!')
else:
    print('Target string not found in collector.py')
