from pysnmp.hlapi import *
import sys

ip = "103.157.79.178"
port = 1611
community = "public"
name_oid = "1.3.6.1.4.1.50224.3.12.2.1.2" # HSGQ Name OID

print(f"Walking OID {name_oid} on {ip}:{port}...")

results = {}
try:
    for (errInd, errStat, errIdx, vBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0), # SNMPv1 for HSGQ
        UdpTransportTarget((ip, port), timeout=5.0, retries=2),
        ContextData(),
        ObjectType(ObjectIdentity(name_oid)),
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
            parts = oid_str.split('.')
            onu_idx = parts[-1]
            results[onu_idx] = val_str
            if "dina" in val_str.lower():
                print(f"FOUND DINA: Index={onu_idx}, Name={val_str}")
except Exception as e:
    print(f"Exception during walk: {e}")

print(f"Walk completed. Total ONUs returned by OLT: {len(results)}")
# print a few samples of names
print("\nFirst 10 ONU names from OLT:")
for idx, name in list(results.items())[:10]:
    print(f"  {idx}: {name}")
