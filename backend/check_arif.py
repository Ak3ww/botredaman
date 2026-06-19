import sqlite3
conn = sqlite3.connect('redaman.db')
rows = conn.execute("SELECT onu_id, olt_id, customer_name FROM onu_name_cache WHERE customer_name LIKE '%arif%' COLLATE NOCASE").fetchall()
for r in rows:
    print(r)
