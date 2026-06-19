from pysnmp.hlapi import *
import sys

ip = "103.157.79.178"
port = 1611
community = "public"
base_oid = "1.3.6.1.4.1.50224"

print(f"Searching for 'dina' or 'lorinsan' in enterprises.50224 on {ip}:{port}...")

found = False
count = 0
try:
    for (errInd, errStat, errIdx, vBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),
        UdpTransportTarget((ip, port), timeout=4.0, retries=2),
        ContextData(),
        ObjectType(ObjectIdentity(base_oid)),
        lexicographicMode=False
    ):
        if errInd:
            print(f"Error: {errInd}")
            break
        if errStat:
            print(f"Error Status: {errStat.prettyPrint()}")
            break
        for vb in vBinds:
            oid_str = vb[0].prettyPrint()
            val_str = vb[1].prettyPrint()
            count += 1
            if any(q in val_str.lower() for q in ["dina", "lorinsan"]):
                print(f"FOUND: OID={oid_str} => Value='{val_str}'")
                found = True
except Exception as e:
    print(f"Exception: {e}")

print(f"Search completed. Scanned {count} OIDs. Found: {found}")
