import sqlite3

conn = sqlite3.connect('C:/BotRedaman/backend/redaman.db')
c = conn.cursor()

# Find the HSGQ olt_id
c.execute("SELECT id FROM olts WHERE brand = 'HSGQ'")
row = c.fetchone()
if row:
    olt_id = row[0]
    c.execute("DELETE FROM onu_name_cache WHERE customer_name = 'RAMADHAN' AND olt_id = ?", (olt_id,))
    c.execute("DELETE FROM alert_states WHERE onu_id = '16777507' AND olt_id = ?", (olt_id,))
    conn.commit()
    print("Deleted stale RAMADHAN from HSGQ")
else:
    print("HSGQ not found")
