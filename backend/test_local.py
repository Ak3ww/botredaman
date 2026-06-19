from pysnmp.hlapi import *

def walk_olt(ip, port, community, base_oid='1.3.6.1.2.1.1.1'):
    print(f"Testing {ip}:{port} (Community: {community})...")
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1), # v2c
        UdpTransportTarget((ip, port), timeout=3.0, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(base_oid)),
        lexicographicMode=False
    ):
        if errorIndication:
            print(f"Error: {errorIndication}")
        else:
            print(f"Success! Response: {varBinds[0][1]}")
        break

if __name__ == "__main__":
    walk_olt('192.168.30.6', 161, 'public') # Test VSOL LOCAL
