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

print("=== VSOL ONUs STATS ===")
for onu_id, d in onus.items():
    col8 = d.get(8, "N/A") # Last Register Time
    col9 = d.get(9, "N/A") # Last Deregister Time
    col10 = d.get(10, "N/A") # Last Deregister Reason
    col11 = d.get(11, "N/A") # Alive Time
    name = d.get(7, "N/A")
    # Let's see if we can determine if it is online or offline based on Last Register vs Last Deregister
    # Note: VSOL time format is YYYY:MM:DD HH:MM:SS or N/A
    is_offline = False
    if col9 != "N/A" and col8 != "N/A":
        # simple string compare might work if format is consistent
        if col9 > col8:
            is_offline = True
    elif col8 == "N/A" or col11 == "N/A" or col11 == "00:00:00" or col11 == "0" or "0 00:00:00" in col11:
        is_offline = True

    if is_offline or col10 != "N/A":
        print(f"ONU {onu_id:5} | Name: {name[:20]:20} | IsOffline: {is_offline} | Alive: {col11} | Reg: {col8} | Dereg: {col9} | Reason: {col10}")
