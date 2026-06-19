import sqlite3
import os

db_path = r"c:\BotRedaman\backend\redaman.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print("Tables:", tables)
        for t in tables:
            tname = t[0]
            try:
                row_count = cursor.execute(f"SELECT COUNT(*) FROM {tname}").fetchone()[0]
                print(f"  Table: {tname}, Rows: {row_count}")
                if tname == 'olts':
                    rows = cursor.execute("SELECT * FROM olts").fetchall()
                    for r in rows:
                        print("    OLT:", r)
            except Exception as e:
                print(f"  Table: {tname}, Error: {e}")
    except Exception as e:
        print("Error listing tables:", e)
    conn.close()
else:
    print("Database not found at", db_path)
