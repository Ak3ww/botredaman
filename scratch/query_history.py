import sqlite3
import os

db_path = r"C:\BotRedaman\backend\redaman.db"
c = sqlite3.connect(db_path)
print("=== Attenuations of SITI HAMIDAH (16777729) on 2026-06-10 ===")
rows = c.execute("""
    SELECT id, rx_power, timestamp 
    FROM attenuations 
    WHERE onu_id = '16777729' AND timestamp LIKE '2026-06-10 %'
    ORDER BY timestamp ASC
""").fetchall()

for row in rows:
    print(row)
