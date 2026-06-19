import re
import collections

onus = collections.defaultdict(dict)
for fn in ['vsol_walk.txt', 'vsol_gpon_real.txt']:
    try:
        with open(fn, encoding='utf-8', errors='ignore') as f:
            for line in f:
                if '37950.1.1.6.1.1.1.1.' in line:
                    parts = line.strip().split(' = ')
                    if len(parts) == 2:
                        oid, val = parts
                        match = re.search(r'37950\.1\.1\.6\.1\.1\.1\.1\.(\d+)\.(\d+)\.(\d+)', oid)
                        if match:
                            col = int(match.group(1))
                            onu_id = f"{match.group(2)}.{match.group(3)}"
                            onus[onu_id][col] = val
    except Exception as e:
        print(f"Error reading {fn}: {e}")

print("=== VSOL GPON ONUs ANALYSIS ===")
# We print details of first 10 ONUs
for onu_id in sorted(onus.keys(), key=lambda x: [int(p) for p in x.split('.')])[:15]:
    d = onus[onu_id]
    name = d.get(7, "Unknown")
    col6 = d.get(6, "?")
    col8 = d.get(8, "?") # Last Register Time
    col9 = d.get(9, "?") # Last Deregister Time
    col10 = d.get(10, "?") # Last Deregister Reason
    col11 = d.get(11, "?") # Alive Time
    print(f"ONU {onu_id:5} | Name: {name[:20]:20} | Col6 (Status?): {col6} | Alive Time: {col11}")
    print(f"  Last Reg  Time: {col8}")
    print(f"  Last Dereg Time: {col9}")
    print(f"  Deregister Reason: {col10}")
    print("-" * 85)
