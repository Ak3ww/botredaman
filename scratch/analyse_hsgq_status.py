import re
import collections

# Load lines from gpon_walk.txt
onus = collections.defaultdict(dict)
with open('gpon_walk.txt', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if '50224.3.12.2.1.' in line:
            parts = line.strip().split(' = ')
            if len(parts) == 2:
                oid, val = parts
                match = re.search(r'50224\.3\.12\.2\.1\.(\d+)\.(\d+)', oid)
                if match:
                    col = int(match.group(1))
                    onu_id = match.group(2)
                    onus[onu_id][col] = val

# Print some online and offline examples
print("=== HSGQ ONUs STATUS COLUMNS ===")
# Sort ONUs by ID
sorted_onus = sorted(onus.keys(), key=int)

for onu in sorted_onus[:10]:
    data = onus[onu]
    name = data.get(2, "Unknown")
    col3 = data.get(3, "?")
    col4 = data.get(4, "?")
    col5 = data.get(5, "?")
    col19 = data.get(19, "?")
    col20 = data.get(20, "?")
    col21 = data.get(21, "?")
    col22 = data.get(22, "?")
    col23 = data.get(23, "?")
    print(f"ONU {onu:8} | Name: {name[:20]:20} | Col3 (Status?): {col3} | Col19: {col19} | Col23 (Alive Time?): {col23}")
    print(f"  Last Up Time  : {col20}")
    print(f"  Last Down Time: {col21}")
    print(f"  Last Down Cause: {col22}")
    print("-" * 80)
