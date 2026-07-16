import openpyxl
import sys
sys.path.append('C:/BotRedaman/backend')
from mikrotik_client import get_mikrotik_data

file_path = 'C:/Users/User/Downloads/pelanggan-export-2026-06-23_18-49-50.xlsx'
wb = openpyxl.load_workbook(file_path)
sheet = wb.active

headers = [str(c.value).strip() if c.value else '' for c in sheet[1]]
pppoe_idx = headers.index('user_pppoe')

name_idx = -1
for i, h in enumerate(headers):
    if 'nama' in h.lower() or 'name' in h.lower() or 'pelanggan' in h.lower():
        name_idx = i
        break

if name_idx == -1:
    name_idx = 1

billing_data = {}
duplicates = []

for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
    val = row[pppoe_idx]
    if val:
        v_str = str(val).strip().upper()
        if v_str.startswith('EMG'):
            name_val = str(row[name_idx]).strip() if row[name_idx] else ''
            
            if v_str in billing_data:
                duplicates.append({
                    'pppoe': v_str,
                    'row1': billing_data[v_str]['row'],
                    'name1': billing_data[v_str]['name'],
                    'row2': row_num,
                    'name2': name_val
                })
            else:
                billing_data[v_str] = {'row': row_num, 'name': name_val}

print('=== DUPLICATE PPPOE IN EXCEL ===')
for d in duplicates:
    print(f"{d['pppoe']} is at Row {d['row1']} (Name: {d['name1']}) AND Row {d['row2']} (Name: {d['name2']})")

print('\n=== MIKROTIK VS EXCEL NAME MISMATCH ===')
active, queues, secrets = get_mikrotik_data()

missing_in_excel = []
mismatch_names = []

for comment, secret_name in secrets.items():
    s_name_upper = secret_name.upper().strip()
    if s_name_upper.startswith('EMG'):
        m_name = comment.replace('Pelanggan:', '').strip()
        
        if s_name_upper not in billing_data:
            if s_name_upper.replace('EMG', '').isdigit():
                missing_in_excel.append((s_name_upper, m_name))
        else:
            excel_name = billing_data[s_name_upper]['name']
            
            # clean both names for comparison
            m_clean = m_name.replace(' ', '').upper()
            e_clean = excel_name.replace(' ', '').upper()
            
            # just a rough check: if first 5 letters don't match
            if m_clean[:5] != e_clean[:5]:
                mismatch_names.append(f"{s_name_upper}: Mikrotik='{m_name}' vs Excel='{excel_name}'")

print(f'\nMissing in Excel: {len(missing_in_excel)}')
for m in missing_in_excel:
    print(m[0], ':', m[1])

print(f'\nName Mismatches (Rough Check): {len(mismatch_names)}')
for m in mismatch_names:
    print(m)
