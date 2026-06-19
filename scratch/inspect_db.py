import sqlite3
import os

db = 'c:\\BotRedaman\\backend\\redaman.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

print("=== OLTS ===")
for r in conn.execute('SELECT * FROM olts').fetchall():
    print(dict(r))

print("=== ALERT STATES COUNT ===")
print(conn.execute('SELECT count(*) FROM alert_states').fetchone()[0])

print("=== CRITICAL ALERTS ===")
for r in conn.execute("SELECT * FROM alert_states WHERE status='CRITICAL'").fetchall():
    print(dict(r))

print("=== ALL ALERTS ===")
for r in conn.execute("SELECT * FROM alert_states LIMIT 10").fetchall():
    print(dict(r))

conn.close()
