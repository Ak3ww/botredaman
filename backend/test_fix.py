import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

import collector

print('--- Menjalankan 1 siklus penarikan data ---')
collector.pull_data_and_alert()

# Check Lasti and Zidan
conn = sqlite3.connect('redaman.db')
rows = conn.execute('''
    SELECT a.customer_name, a.rx_power 
    FROM attenuations a 
    WHERE (customer_name LIKE "%LASTI%" OR customer_name LIKE "%ZIDAN%")
    ORDER BY a.timestamp DESC LIMIT 4
''').fetchall()
print("\nHasil terbaru dari DB:")
for r in rows:
    print(f"  {r[0]}: {r[1]} dBm")
conn.close()
