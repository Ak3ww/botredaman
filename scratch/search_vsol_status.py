with open('vsol_walk.txt', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print("=== SEARCHING vsol_walk.txt FOR STATE/STATUS ===")
for line in lines:
    line_lower = line.lower()
    if 'state' in line_lower or 'status' in line_lower or 'phase' in line_lower:
        # Check if there is an OID/value pair
        if '37950' in line and len(line.strip()) < 120:
            print(line.strip())
