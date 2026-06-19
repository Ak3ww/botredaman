import collections
import re

patterns = collections.defaultdict(set)
for fn in ['vsol_walk.txt', 'vsol_gpon_real.txt']:
    try:
        with open(fn, encoding='utf-8', errors='ignore') as f:
            for line in f:
                if '37950.1.1.6.1.1.' in line:
                    parts = line.strip().split(' = ')
                    if len(parts) == 2:
                        oid, val = parts
                        # Match 1.3.6.1.4.1.37950.1.1.6.1.1.A.B.C...
                        match = re.search(r'37950\.1\.1\.6\.1\.1\.(\d+)\.(\d+)\.(\d+)', oid)
                        if match:
                            table = match.group(1)
                            col = match.group(2)
                            patterns[table].add(col)
    except Exception as e:
        print(f"Error reading {fn}: {e}")

print("=== VSOL Tables under 37950.1.1.6.1.1 ===")
for t in sorted(patterns.keys(), key=int):
    print(f"Table {t} columns: {sorted(list(patterns[t]), key=int)}")
