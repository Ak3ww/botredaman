import sqlite3
c = sqlite3.connect('redaman.db')

print("=== ALERT STATES (non-NORMAL) ===")
rows = c.execute('''
    SELECT s.onu_id, s.customer_name, s.status, s.last_alert_time, s.last_offline_reason,
           (SELECT a.rx_power FROM attenuations a WHERE a.onu_id=s.onu_id ORDER BY a.timestamp DESC LIMIT 1)
    FROM alert_states s 
    WHERE s.status != 'NORMAL'
    ORDER BY s.last_alert_time DESC LIMIT 15
''').fetchall()
for r in rows:
    print(r)

print("\n=== LASTI last 5 attenuations ===")
rows2 = c.execute('''
    SELECT rx_power, timestamp FROM attenuations 
    WHERE customer_name LIKE '%LASTI%'
    ORDER BY timestamp DESC LIMIT 5
''').fetchall()
for r in rows2:
    print(r)
