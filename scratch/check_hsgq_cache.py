import sqlite3
import os

db_path = r"c:\BotRedaman\backend\redaman.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Latest 10 HSGQ Cache updates ---")
    rows = cursor.execute("SELECT onu_id, customer_name, last_updated FROM onu_name_cache WHERE olt_id = 1 ORDER BY last_updated DESC LIMIT 10").fetchall()
    for r in rows:
        print(r)
        
    conn.close()
else:
    print("Database not found")
