import os

walk_files = [
    r"c:\BotRedaman\gpon_walk.txt",
    r"c:\BotRedaman\hsgq_scan.txt"
]

target_names = ["SITI HAMIDAH", "ATIN NGATINI", "ONT02/026"]

for wf in walk_files:
    if os.path.exists(wf):
        print(f"--- Searching in {wf} ---")
        with open(wf, "r", errors="ignore") as f:
            for line in f:
                for name in target_names:
                    if name.lower() in line.lower():
                        print(f"Found '{name}': {line.strip()}")
    else:
        print(f"{wf} not found")
