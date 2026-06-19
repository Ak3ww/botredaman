import sqlite3, datetime, time, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\BotRedaman\backend'
c = sqlite3.connect(os.path.join(BASE, 'redaman.db'))

print("=== STATUS BOT ===\n")

# 1. Last reminder
LR = os.path.join(BASE, 'last_reminder.txt')
if os.path.exists(LR):
    ts = float(open(LR).read().strip())
    dt = datetime.datetime.fromtimestamp(ts)
    secs_ago = time.time() - ts
    print(f"Last reminder    : {dt.strftime('%Y-%m-%d %H:%M:%S')} ({secs_ago/60:.1f} menit lalu)")
else:
    print("Last reminder    : TIDAK ADA (belum pernah kirim)")

# 2. Config
cfg_file = os.path.join(BASE, 'config.json')
if os.path.exists(cfg_file):
    cfg = json.load(open(cfg_file))
    print(f"Reminder interval: {cfg.get('reminder_minutes', 60)} menit")
    print(f"Dashboard URL    : {cfg.get('dashboard_url', '?')}")
else:
    print("config.json      : TIDAK ADA (default 60 menit)")

# 3. Status ONU
print()
rows = c.execute("SELECT status, COUNT(*) FROM alert_states GROUP BY status").fetchall()
print("Status ONU:")
for r in rows:
    print(f"  {r[0]:10} : {r[1]} ONU")

# 4. Attenuations terbaru
print()
last_att = c.execute("SELECT MAX(timestamp) FROM attenuations").fetchone()[0]
print(f"Attenuation terakhir: {last_att}")

# 5. Cek apakah ada masalah schema (alert_states PK)
pk_cols = [r[1] for r in c.execute('PRAGMA table_info(alert_states)').fetchall() if r[5] > 0]
print(f"alert_states PK  : {pk_cols}")

# 6. Total rows
att_count = c.execute("SELECT COUNT(*) FROM attenuations").fetchone()[0]
cache_count = c.execute("SELECT COUNT(*) FROM onu_name_cache").fetchone()[0]
print(f"\nAttenuations rows: {att_count:,}")
print(f"Cache rows       : {cache_count}")
