import sqlite3

conn = sqlite3.connect('c:\\BotRedaman\\backend\\redaman.db')
cursor = conn.cursor()

# Get list of tables
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("Tables in Database:")
for t in tables:
    t_name = t[0]
    print(f"\nTable: {t_name}")
    # Get column definitions
    columns = cursor.execute(f"PRAGMA table_info({t_name});").fetchall()
    for col in columns:
        print(f"  Column: {col[1]} ({col[2]})")

conn.close()
