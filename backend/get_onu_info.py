from pysnmp.hlapi import *
import sys

def get_oid(ip, port, community, oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community, mpModel=0),
               UdpTransportTarget((ip, port), timeout=1.0, retries=1),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )
    if errorIndication or errorStatus:
        return None
    for varBind in varBinds:
        if varBind[1] != "" and "No Such" not in str(varBind[1]):
            return str(varBind[1])
    return None

def scan_onu(ip, port, community):
    print(f"Scanning ONU 1.1 on {ip}...")
    for x in range(1, 10):
        for y in range(1, 20):
            oid = f"1.3.6.1.4.1.37950.1.1.6.1.1.{x}.1.{y}.1.1"
            val = get_oid(ip, port, community, oid)
            if val:
                print(f"OID {oid} = {val}")

if __name__ == "__main__":
    scan_onu('192.168.30.6', 161, 'public')
