import sqlite3

conn = sqlite3.connect(r'C:\BotRedaman\backend\redaman.db')
c = conn.cursor()

print("--- Alert States for ATIN ---")
c.execute("SELECT onu_id, olt_id, customer_name, status, last_alert_time, last_offline_reason, last_up_time, last_down_time, alive_time FROM alert_states WHERE customer_name LIKE '%ATIN%'")
for r in c.fetchall():
    print(r)

print("\n--- Recent Connection Events for ATIN ---")
c.execute("SELECT timestamp, event_type, reason, rx_power FROM connection_events WHERE customer_name LIKE '%ATIN%' ORDER BY id DESC LIMIT 10")
for r in c.fetchall():
    print(r)

conn.close()
