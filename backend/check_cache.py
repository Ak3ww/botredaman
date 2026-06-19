import sqlite3

conn = sqlite3.connect(r'C:\BotRedaman\backend\redaman.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM onu_name_cache WHERE pppoe_username NOT LIKE 'EMG%' AND pppoe_username NOT LIKE 'FAS%' AND pppoe_username NOT LIKE '%fasum%'")
other = c.fetchone()[0]

print(f'Total other formats: {other}')
if other > 0:
    print('\n--- Sample other bindings ---')
    c.execute("SELECT onu_id, customer_name, pppoe_username FROM onu_name_cache WHERE pppoe_username NOT LIKE 'EMG%' AND pppoe_username NOT LIKE 'FAS%' AND pppoe_username NOT LIKE '%fasum%' LIMIT 10")
    for r in c.fetchall():
        print(f"  ONU {r[0]}: {r[1]} -> {r[2]}")

conn.close()
