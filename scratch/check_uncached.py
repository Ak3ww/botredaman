import sqlite3
import os

db_path = r"c:\BotRedaman\backend\redaman.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- ONU IDs in alert_states but missing from onu_name_cache ---")
    rows = cursor.execute("""
        SELECT a.onu_id, a.customer_name, a.status 
        FROM alert_states a
        LEFT JOIN onu_name_cache c ON a.onu_id = c.onu_id AND a.olt_id = c.olt_id
        WHERE a.olt_id = 1 AND c.onu_id IS NULL
    """).fetchall()
    for r in rows:
        print(r)
        
    print("\n--- ONU IDs in recent attenuations but missing from onu_name_cache ---")
    rows2 = cursor.execute("""
        SELECT DISTINCT a.onu_id 
        FROM attenuations a
        LEFT JOIN onu_name_cache c ON a.onu_id = c.onu_id AND a.olt_id = c.olt_id
        WHERE a.olt_id = 1 AND c.onu_id IS NULL
        ORDER BY a.timestamp DESC LIMIT 10
    """).fetchall()
    for r in rows2:
        print(r)
        
    conn.close()
else:
    print("Database not found")
