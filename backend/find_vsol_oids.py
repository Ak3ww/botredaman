import re

def analyze_walk(filename):
    print(f"Analyzing {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    potential_powers = []
    potential_names = []
    
    for line in lines:
        if " = " not in line: continue
        parts = line.strip().split(" = ", 1)
        if len(parts) < 2: continue
        oid, val = parts[0], parts[1]
        
        # Cari nilai power (biasanya antara -400 sampai -100, atau 100 sampai 400)
        # Atau jika desimal (contoh: -25.4)
        if re.match(r'^-?\d+(\.\d+)?$', val):
            num = float(val)
            if -400 <= num <= -100 or -40 <= num <= -10:
                potential_powers.append((oid, val))
        
        # Cari nama (string yang lebih dari 3 huruf tapi bukan OID dan bukan FFFFFF)
        if re.match(r'^[a-zA-Z0-9 _-]{4,}$', val) and not val.startswith("0x") and not val.startswith("FFFFFF") and "1000" not in val:
            potential_names.append((oid, val))
            
    print(f"\nPotential Rx Powers ({len(potential_powers)} found):")
    for oid, val in potential_powers[:20]:
        print(f"  {oid} = {val}")
        
    print(f"\nPotential Names ({len(potential_names)} found):")
    for oid, val in potential_names[:20]:
        print(f"  {oid} = {val}")

if __name__ == "__main__":
    analyze_walk("c:\\BotRedaman\\vsol_gpon_real.txt")
