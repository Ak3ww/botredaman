import json
from routeros_client import RouterOSClient

try:
    with open('c:/BotRedaman/backend/config.json', 'r') as f:
        config = json.load(f)

    client = RouterOSClient(
        host=config['mikrotik_host'],
        port=config['mikrotik_port'],
        user=config['mikrotik_username'],
        password=config['mikrotik_password']
    )
    
    nat_rules = client.path('/ip/firewall/nat').get()
    print("NAT Rules:")
    for rule in nat_rules:
        if rule.get('action') == 'dst-nat' and rule.get('to-addresses') in ['10.10.10.2', '10.10.10.3', '10.10.10.4']:
            print(f"Port {rule.get('dst-port')} -> {rule.get('to-addresses')}:{rule.get('to-ports')}")
            
except Exception as e:
    print(f"Error: {e}")
