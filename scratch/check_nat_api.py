import routeros_api
import pprint

connection = routeros_api.RouterOsApiPool('103.157.79.178', username='billinghub.id', password='@eugine0909@', port=8520, plaintext_login=True)
api = connection.get_api()

nat_rules = api.get_resource('/ip/firewall/nat').get()
print("NAT Rules:")
for rule in nat_rules:
    if rule.get('action') == 'dst-nat':
        print(f"[{rule.get('id')}] {rule.get('dst-address', 'ANY')} {rule.get('protocol', 'ANY')}:{rule.get('dst-port', 'ANY')} -> {rule.get('to-addresses', 'ANY')}:{rule.get('to-ports', 'ANY')}")

connection.disconnect()
