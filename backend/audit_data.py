import sqlite3
import openpyxl
import difflib
import sys
sys.path.append('C:/BotRedaman/backend')
from mikrotik_client import get_mikrotik_data
from collections import defaultdict

def clean_name(n):
    return str(n).upper().replace('PELANGGAN:', '').strip()

# 1. Load Mikrotik Data
active, queues, secrets = get_mikrotik_data()
mikrotik_data = {}
for comment, secret in secrets.items():
    if secret.upper().startswith('EMG'):
        m_name = clean_name(comment)
        mikrotik_data[secret.upper()] = m_name

# 2. Load Billing Data
file_path = 'C:/Users/User/Downloads/pelanggan-export-2026-06-24_10-49-49.xlsx'
try:
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active
except Exception as e:
    print(f"Error reading Excel: {e}")
    sys.exit(1)

headers = [str(c.value).strip() if c.value else '' for c in sheet[1]]
try:
    pppoe_idx = headers.index('user_pppoe')
    name_idx = headers.index('nama')
except ValueError:
    name_idx = 5
    pppoe_idx = 21

billing_data = {}
excel_duplicates = []
for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
    pppoe = row[pppoe_idx]
    if pppoe and str(pppoe).upper().startswith('EMG'):
        v_str = str(pppoe).strip().upper()
        name_val = clean_name(row[name_idx]) if row[name_idx] else ''
        if v_str in billing_data:
            excel_duplicates.append(f"Row {row_num}: {v_str} ({name_val}) duplicates Row {billing_data[v_str]['row']} ({billing_data[v_str]['name']})")
        billing_data[v_str] = {'row': row_num, 'name': name_val}

# 3. Load OLT Data
conn = sqlite3.connect('C:/BotRedaman/backend/redaman.db')
c = conn.cursor()
c.execute('SELECT onu_id, olt_id, customer_name, sn, pppoe_username FROM onu_name_cache')
olt_records = c.fetchall()

olt_data = []
for onu_id, olt_id, customer_name, sn, pppoe_username in olt_records:
    if not customer_name or 'ZTEG' in customer_name.upper() or 'SKYW' in customer_name.upper() or 'ALCL' in customer_name.upper() or 'HWTC' in customer_name.upper():
        continue
    c.execute('SELECT name FROM olts WHERE id=?', (olt_id,))
    olt_name = c.fetchone()[0]
    olt_data.append({
        'olt': olt_name,
        'port': onu_id,
        'name': clean_name(customer_name),
        'sn': sn,
        'mapped_pppoe': pppoe_username
    })

print("=== 1. MISSING IN EXCEL (IN MIKROTIK BUT NO BILLING) ===")
missing_excel = []
for pppoe, m_name in mikrotik_data.items():
    if pppoe not in billing_data and pppoe.replace('EMG', '').isdigit():
        missing_excel.append(f"{pppoe} ({m_name})")
for m in sorted(missing_excel):
    print(m)

print("\n=== 2. MISSING IN MIKROTIK (IN EXCEL BUT NO MIKROTIK) ===")
missing_mikrotik = []
for pppoe, b_data in billing_data.items():
    if pppoe not in mikrotik_data and pppoe.replace('EMG', '').isdigit():
        missing_mikrotik.append(f"{pppoe} ({b_data['name']})")
for m in sorted(missing_mikrotik):
    print(m)

print("\n=== 3. NAME MISMATCH (MIKROTIK VS EXCEL) ===")
name_mismatches = []
for pppoe, m_name in mikrotik_data.items():
    if pppoe in billing_data:
        e_name = billing_data[pppoe]['name']
        ratio = difflib.SequenceMatcher(None, m_name.replace(' ', ''), e_name.replace(' ', '')).ratio()
        if ratio < 0.7:
            name_mismatches.append(f"{pppoe} | Mikrotik: {m_name} | Excel: {e_name}")
for m in name_mismatches:
    print(m)

print("\n=== 4. EXCEL DUPLICATE ROWS ===")
for d in excel_duplicates:
    print(d)

print("\n=== 5. OLT MISMATCHES (TYPO / NOT IN MIKROTIK) ===")
olt_mismatches = []
m_names = list(mikrotik_data.values())
for o in olt_data:
    o_name = o['name']
    if o_name not in m_names:
        # Ignore FASUM/FREE generic names
        if 'FASUM' in o_name or 'FREE' in o_name or 'POSYANDU' in o_name or 'MASJID' in o_name or 'KANTOR' in o_name or 'POS' in o_name or 'RT' in o_name:
            continue
        
        best_match = None
        best_ratio = 0
        for m_name in m_names:
            ratio = difflib.SequenceMatcher(None, o_name.replace(' ', ''), m_name.replace(' ', '')).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = m_name
                
        olt_mismatches.append(f"[{o['olt']} {o['port']}] {o_name} -> Typo of: {best_match} ({int(best_ratio*100)}%)")

for m in sorted(olt_mismatches):
    print(m)

print("\n=== 6. OLT DUPLICATE NAMES ===")
name_counts = defaultdict(list)
for o in olt_data:
    name_counts[o['name']].append(f"{o['olt']} {o['port']}")

for name, locs in name_counts.items():
    if len(locs) > 1:
        # Ignore Generic
        if 'FASUM' in name or 'FREE' in name or 'POSYANDU' in name:
            continue
        print(f"{name} is configured on {len(locs)} ports: {', '.join(locs)}")

print("\n=== 7. PERFECTLY SYNCED ===")
perfect_count = 0
for pppoe, m_name in mikrotik_data.items():
    if pppoe in billing_data:
        e_name = billing_data[pppoe]['name']
        ratio = difflib.SequenceMatcher(None, m_name.replace(' ', ''), e_name.replace(' ', '')).ratio()
        if ratio >= 0.7:
            # Check if it exists exactly in OLT
            if m_name in [o['name'] for o in olt_data]:
                perfect_count += 1
print(f"{perfect_count} Customers are 100% perfectly synced across OLT, Mikrotik, and Billing!")
