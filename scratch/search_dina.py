import sqlite3
import os

db_path = r"c:\BotRedaman\backend\redaman.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Searching onu_name_cache ---")
    rows = cursor.execute("SELECT * FROM onu_name_cache WHERE customer_name LIKE '%dina%'").fetchall()
    for r in rows:
        print(r)
        
    print("\n--- Searching alert_states ---")
    rows2 = cursor.execute("SELECT * FROM alert_states WHERE customer_name LIKE '%dina%'").fetchall()
    for r in rows2:
        print(r)
        
    print("\n--- Searching attenuations (sample of names) ---")
    # check columns in attenuations
    cols = [r[1] for r in cursor.execute("PRAGMA table_info(attenuations)").fetchall()]
    print("Attenuations columns:", cols)
    if 'customer_name' in cols:
        rows3 = cursor.execute("SELECT * FROM attenuations WHERE customer_name LIKE '%dina%' LIMIT 5").fetchall()
        for r in rows3:
            print(r)
            
    conn.close()
else:
    print("Database not found")
