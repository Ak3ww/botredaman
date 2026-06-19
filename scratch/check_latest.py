import sqlite3
import os

db_path = r"c:\BotRedaman\backend\redaman.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Latest 5 Attenuations ---")
    rows = cursor.execute("SELECT id, olt_id, onu_id, rx_power, timestamp FROM attenuations ORDER BY id DESC LIMIT 5").fetchall()
    for r in rows:
        print(r)
        
    print("\n--- Latest 5 onu_name_cache entries ---")
    rows2 = cursor.execute("SELECT * FROM onu_name_cache ORDER BY last_updated DESC LIMIT 5").fetchall()
    for r in rows2:
        print(r)
        
    conn.close()
else:
    print("Database not found")
