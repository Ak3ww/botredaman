import sqlite3
import os

db_path = r"c:\BotRedaman\backend\redaman.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Latest 5 HSGQ Attenuations ---")
    rows = cursor.execute("SELECT id, onu_id, rx_power, timestamp FROM attenuations WHERE olt_id = 1 ORDER BY id DESC LIMIT 5").fetchall()
    for r in rows:
        print(r)
        
    print("\n--- OLT 1 (HSGQ) Status in alert_states (Latest 5) ---")
    rows2 = cursor.execute("SELECT onu_id, customer_name, status, last_alert_time FROM alert_states WHERE olt_id = 1 ORDER BY last_alert_time DESC LIMIT 5").fetchall()
    for r in rows2:
        print(r)
        
    conn.close()
else:
    print("Database not found")
