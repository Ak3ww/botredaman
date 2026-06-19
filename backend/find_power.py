import re

def analyze_power(filename):
    print(f"Mencari Rx Power di {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        if " = " not in line: continue
        parts = line.strip().split(" = ", 1)
        if len(parts) < 2: continue
        oid, val = parts[0], parts[1]
        
        if re.match(r'^-?\d+(\.\d+)?$', val):
            num = float(val)
            if -450 <= num <= -100 or -45 <= num <= -10:
                print(f"Potential Power: {oid} = {val}")

if __name__ == "__main__":
    analyze_power("c:\\BotRedaman\\vsol_gpon_real.txt")
