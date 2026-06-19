"""
migrate_db.py — Migrasi schema database NOC Redaman
Aman dijalankan berulang kali (idempotent).
"""
import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

DB = 'redaman.db'
conn = sqlite3.connect(DB, timeout=30)
c = conn.cursor()
c.execute("PRAGMA journal_mode=WAL")  # Izinkan baca bersamaan saat write

print("=== Migrasi Database NOC Redaman ===\n")

# 1. Tambah INDEX attenuations untuk query cepat
print("[1/5] Membuat index pada attenuations...")
try:
    c.execute('''CREATE INDEX IF NOT EXISTS idx_att_olt_onu_ts 
                 ON attenuations(olt_id, onu_id, timestamp DESC)''')
    print("      ✅ Index dibuat.")
except Exception as e:
    print(f"      ⚠️  {e}")

# 2. Hapus kolom customer_name dari attenuations (jika masih ada)
# SQLite < 3.35 tidak support DROP COLUMN, jadi kita biarkan tapi tidak pakai
print("[2/5] Memeriksa kolom attenuations...")
cols = [r[1] for r in c.execute('PRAGMA table_info(attenuations)').fetchall()]
print(f"      Kolom saat ini: {cols}")

# 3. Fix alert_states PRIMARY KEY menjadi (onu_id, olt_id)
# Cek apakah sudah composite PK
print("[3/5] Memeriksa primary key alert_states...")
pk_cols = [r[1] for r in c.execute('PRAGMA table_info(alert_states)').fetchall() if r[5] > 0]
print(f"      PK saat ini: {pk_cols}")

if pk_cols == ['onu_id']:
    print("      PK hanya onu_id — migrasi ke (onu_id, olt_id)...")
    # Backup data lama
    c.execute('''CREATE TABLE IF NOT EXISTS alert_states_backup AS SELECT * FROM alert_states''')
    # Buat tabel baru dengan composite PK
    c.execute('''CREATE TABLE IF NOT EXISTS alert_states_new (
        onu_id              TEXT NOT NULL,
        olt_id              INTEGER NOT NULL,
        customer_name       TEXT,
        status              TEXT NOT NULL DEFAULT 'NORMAL',
        last_alert_time     DATETIME,
        last_offline_reason TEXT,
        PRIMARY KEY (onu_id, olt_id),
        FOREIGN KEY(olt_id) REFERENCES olts(id)
    )''')
    # Copy data, pakai COALESCE untuk olt_id yang mungkin NULL
    c.execute('''INSERT OR IGNORE INTO alert_states_new 
                 (onu_id, olt_id, customer_name, status, last_alert_time, last_offline_reason)
                 SELECT onu_id, COALESCE(olt_id, 1), customer_name, status, last_alert_time, last_offline_reason
                 FROM alert_states_backup''')
    count = c.execute('SELECT COUNT(*) FROM alert_states_new').fetchone()[0]
    # Ganti tabel
    c.execute('DROP TABLE alert_states')
    c.execute('ALTER TABLE alert_states_new RENAME TO alert_states')
    print(f"      ✅ Migrasi selesai — {count} baris dipindahkan.")
elif set(pk_cols) == {'onu_id', 'olt_id'} or 'olt_id' in pk_cols:
    print("      ✅ Sudah composite PK (onu_id, olt_id). Tidak perlu migrasi.")
else:
    print(f"      ℹ️  PK: {pk_cols} — tidak perlu diubah.")

# 3b. Pastikan alert_states memiliki kolom last_up_time, last_down_time, alive_time
print("[3b] Memeriksa kolom alert_states...")
alert_cols = [r[1] for r in c.execute('PRAGMA table_info(alert_states)').fetchall()]
for col, ctype in [('last_up_time', 'TEXT'), ('last_down_time', 'TEXT'), ('alive_time', 'TEXT')]:
    if col not in alert_cols:
        c.execute(f"ALTER TABLE alert_states ADD COLUMN {col} {ctype}")
        print(f"      ✅ Kolom '{col}' ditambahkan ke alert_states.")
    else:
        print(f"      ✅ Kolom '{col}' sudah ada di alert_states.")

# 4. Pastikan onu_name_cache sudah punya sn & firmware_version
print("[4/5] Memeriksa kolom onu_name_cache...")
cache_cols = [r[1] for r in c.execute('PRAGMA table_info(onu_name_cache)').fetchall()]
for col, ctype in [('sn', 'TEXT'), ('firmware_version', 'TEXT')]:
    if col not in cache_cols:
        c.execute(f'ALTER TABLE onu_name_cache ADD COLUMN {col} {ctype}')
        print(f"      ✅ Kolom '{col}' ditambahkan.")
    else:
        print(f"      ✅ Kolom '{col}' sudah ada.")

# 5. Pruning attenuations > 14 hari (bersihkan data lawas)
print("[5/5] Pruning attenuations > 14 hari...")
before = c.execute('SELECT COUNT(*) FROM attenuations').fetchone()[0]
c.execute("DELETE FROM attenuations WHERE timestamp < datetime('now', '-14 days', 'localtime')")
after = c.execute('SELECT COUNT(*) FROM attenuations').fetchone()[0]
print(f"      ✅ Hapus {before - after} baris lama. Sisa: {after} baris.")

conn.commit()
conn.close()
print("\n=== Migrasi Selesai! ===")
