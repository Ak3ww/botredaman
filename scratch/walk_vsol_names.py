from pysnmp.hlapi import *
import sys

ip = "192.168.30.6"
port = 161
community = "public"
name_oid = "1.3.6.1.4.1.37950.1.1.6.1.1.1.1.7" # VSOL Name OID

print(f"Walking OID {name_oid} on {ip}:{port}...")

results = {}
try:
    for (errInd, errStat, errIdx, vBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1), # SNMPv2c for VSOL
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
            onu_idx = f"{parts[-2]}.{parts[-1]}"
            results[onu_idx] = val_str
            if "dina" in val_str.lower():
                print(f"FOUND DINA ON VSOL: Index={onu_idx}, Name={val_str}")
except Exception as e:
    print(f"Exception during walk: {e}")

print(f"Walk completed. Total ONUs returned by VSOL: {len(results)}")
print("\nFirst 10 ONU names from VSOL:")
for idx, name in list(results.items())[:10]:
    print(f"  {idx}: {name}")
