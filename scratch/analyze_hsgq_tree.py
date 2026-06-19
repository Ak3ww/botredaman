import re
import os

walk_file = r"c:\BotRedaman\gpon_walk.txt"
if os.path.exists(walk_file):
    print("Analyzing GPON OID patterns in walk file...")
    oids = {}
    with open(walk_file, "r", errors="ignore") as f:
        for line in f:
            # Match lines like: enterprises.50224.3.12.x.y.z...
            m = re.search(r'enterprises\.50224\.3\.12\.([\d\.]+)\.(\d+)\s+=\s+(.*)', line)
            if m:
                table_path = m.group(1)
                idx = m.group(2)
                val = m.group(3)
                key = f"3.12.{table_path}"
                if key not in oids:
                    oids[key] = []
                oids[key].append((idx, val))
                
    for path, items in oids.items():
        print(f"Table path: {path} - Count: {len(items)}")
        print("  Samples:")
        for idx, val in items[:5]:
            print(f"    {idx} => {val}")
else:
    print("Walk file not found")
