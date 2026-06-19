import re

def find_macs(filename):
    print(f"Mencari GPON SN di {filename}...")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            if " = " not in line: continue
            parts = line.strip().split(" = ", 1)
            if len(parts) < 2: continue
            oid, val = parts[0], parts[1]
            
            if val.startswith("0x") and len(val) >= 10:
                print(f"Found Hex: {oid} = {val}")
            elif any(vendor in val for vendor in ["VSOL", "ZTEG", "HWTC", "ALCL", "FHTT"]):
                print(f"Found GPON SN: {oid} = {val}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_macs("c:\\BotRedaman\\vsol_walk.txt")
