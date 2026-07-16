import sqlite3
import datetime

DB_FILE = 'redaman.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Hapus tabel lama karena kita mengubah struktur (hanya untuk tahap development)
    cursor.execute('DROP TABLE IF EXISTS alert_states')
    cursor.execute('DROP TABLE IF EXISTS attenuations')
    cursor.execute('DROP TABLE IF EXISTS olts')
    
    # Tabel untuk menyimpan daftar OLT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS olts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ip_port TEXT NOT NULL,
            brand TEXT NOT NULL,
            community TEXT DEFAULT 'public'
        )
    ''')
    
    # Tabel untuk menyimpan hasil redaman (Optical Power) dari pelanggan
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attenuations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            olt_id INTEGER,
            port_name TEXT NOT NULL,
            onu_id TEXT NOT NULL,
            customer_name TEXT, 
            rx_power REAL,
            tx_power REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(olt_id) REFERENCES olts(id)
        )
    ''')
    
    # Tabel untuk melacak status notifikasi Telegram (Alert State)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_states (
            onu_id TEXT PRIMARY KEY,
            olt_id INTEGER,
            customer_name TEXT,
            status TEXT NOT NULL,
            last_alert_time DATETIME,
            last_offline_reason TEXT,
            last_up_time DATETIME,
            last_down_time DATETIME,
            alive_time TEXT,
            FOREIGN KEY(olt_id) REFERENCES olts(id)
        )
    ''')
    
    # Tabel untuk cache nama pelanggan dari OLT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS onu_name_cache (
            onu_id TEXT NOT NULL,
            olt_id INTEGER NOT NULL,
            customer_name TEXT,
            sn TEXT,
            firmware_version TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (onu_id, olt_id),
            FOREIGN KEY(olt_id) REFERENCES olts(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_olt(name, ip_port, brand, community='public'):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO olts (name, ip_port, brand, community) VALUES (?, ?, ?, ?)', 
                   (name, ip_port, brand, community))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    # Otomatis isi kembali OLT HSGQ
    add_olt('HSGQ-G02ID', '103.157.79.178:1611', 'HSGQ', 'public')
    print("Database SQLite dengan Identitas Pelanggan berhasil dibuat!")
