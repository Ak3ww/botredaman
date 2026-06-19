import sqlite3

c = sqlite3.connect(r"C:\BotRedaman\backend\redaman.db")

print("=== SITI HAMIDAH ===")
rows = c.execute("""
    SELECT onu_id, customer_name, status, last_offline_reason, last_up_time, last_down_time, alive_time 
    FROM alert_states 
    WHERE customer_name LIKE '%Hamidah%'
""").fetchall()
for row in rows:
    print(row)

print("\n=== SOME OTHER ONUs WITH METRICS ===")
rows = c.execute("""
    SELECT onu_id, customer_name, status, last_offline_reason, last_up_time, last_down_time, alive_time 
    FROM alert_states 
    WHERE last_up_time IS NOT NULL AND last_up_time != '-'
    LIMIT 5
""").fetchall()
for row in rows:
    print(row)
