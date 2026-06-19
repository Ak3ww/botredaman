import re
import os

walk_file = r"c:\BotRedaman\gpon_walk.txt"
if os.path.exists(walk_file):
    print("Listing columns for 50224.3.12.2.1...")
    columns = set()
    with open(walk_file, "r", errors="ignore") as f:
        for line in f:
            m = re.search(r'enterprises\.50224\.3\.12\.2\.1\.(\d+)\.(\d+)\s+=\s+(.*)', line)
            if m:
                columns.add(m.group(1))
    
    print("Found column indices:", sorted([int(c) for c in columns]))
    
    # Print the values of these columns for a sample ONU (e.g. index 16777472)
    sample_onu = "16777472"
    print(f"\nValues for sample ONU {sample_onu}:")
    with open(walk_file, "r", errors="ignore") as f:
        for line in f:
            if sample_onu in line:
                m = re.search(r'enterprises\.50224\.3\.12\.2\.1\.(\d+)\.16777472\s+=\s+(.*)', line)
                if m:
                    print(f"  Col {m.group(1)}: {m.group(2)}")
else:
    print("Walk file not found")
