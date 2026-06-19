import sqlite3
import os

db_path = r"c:\BotRedaman\backend\redaman.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Cache counts by OLT ---")
    rows = cursor.execute("SELECT olt_id, COUNT(*) FROM onu_name_cache GROUP BY olt_id").fetchall()
    for r in rows:
        print(f"OLT ID: {r[0]}, Cache Count: {r[1]}")
        
    print("\n--- OLTs in DB ---")
    olts = cursor.execute("SELECT * FROM olts").fetchall()
    for o in olts:
        print(o)
        
    conn.close()
else:
    print("Database not found")
