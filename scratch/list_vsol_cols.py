import collections
import re

sub_oids = collections.defaultdict(list)
# We will search both vsol_walk.txt and vsol_gpon_real.txt
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
                            col = match.group(1)
                            onu_id = f"{match.group(2)}.{match.group(3)}"
                            sub_oids[col].append((onu_id, val))
    except Exception as e:
        print(f"Error reading {fn}: {e}")

print("=== VSOL ONU TABLE (37950.1.1.6.1.1.1.1.X) ===")
for col in sorted(sub_oids.keys(), key=int):
    items = sub_oids[col]
    print(f"Column {col:2}: {len(items):3} items | Examples:")
    for onu, val in items[:3]:
        print(f"  ONU {onu} -> {val}")
