from pysnmp.hlapi import *
import sys

ip = "103.157.79.178"
port = 1611
community = "public"
name_oid = "1.3.6.1.4.1.50224.3.12.2.1.2"

results = []
try:
    for (errInd, errStat, errIdx, vBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),
        UdpTransportTarget((ip, port), timeout=5.0, retries=2),
        ContextData(),
        ObjectType(ObjectIdentity(name_oid)),
        lexicographicMode=False
    ):
        if errInd or errStat:
            break
        for vb in vBinds:
            oid_str = vb[0].prettyPrint()
            val_str = vb[1].prettyPrint()
            parts = oid_str.split('.')
            results.append((parts[-1], val_str.strip()))
except Exception as e:
    print("Error:", e)

# Sort by name
results.sort(key=lambda x: x[1].lower())
print(f"Total OLT ONUs: {len(results)}")
for idx, name in results:
    if any(q in name.lower() for q in ["din", "lor", "rin", "san"]):
        print(f"  MATCH: Index={idx}, Name='{name}'")
    else:
        # just print a few characters
        pass

print("\n--- ALL NAMES ---")
for i, (idx, name) in enumerate(results):
    print(f"{i+1:3d}. {idx}: '{name}'")
