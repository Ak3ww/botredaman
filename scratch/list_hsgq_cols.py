import collections
import re

sub_oids = collections.defaultdict(list)
with open('gpon_walk.txt', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if '50224.3.12.2.1.' in line:
            parts = line.strip().split(' = ')
            if len(parts) == 2:
                oid, val = parts
                match = re.search(r'50224\.3\.12\.2\.1\.(\d+)\.(\d+)', oid)
                if match:
                    col = match.group(1)
                    onu_id = match.group(2)
                    sub_oids[col].append((onu_id, val))

print("=== HSGQ ONU TABLE (50224.3.12.2.1.X) ===")
for col in sorted(sub_oids.keys(), key=int):
    items = sub_oids[col]
    print(f"Column {col:2}: {len(items):3} items | Examples:")
    for onu, val in items[:3]:
        print(f"  ONU {onu} -> {val}")
