import sqlite3

def generate_unbound_report():
    conn = sqlite3.connect(r'C:\BotRedaman\backend\redaman.db')
    c = conn.cursor()

    c.execute("""
        SELECT olt_id, onu_id, customer_name, pppoe_username 
        FROM onu_name_cache 
        WHERE pppoe_username NOT LIKE 'EMG%' 
          AND pppoe_username NOT LIKE 'FAS%'
        ORDER BY olt_id, onu_id
    """)
    
    rows = c.fetchall()
    conn.close()

    if not rows:
        return "Semua ONU berhasil di-bind ke Mikrotik! (Format EMG/FAS)"

    md = "### Daftar ONU yang Gagal Ter-bind ke Akun Mikrotik (Tidak ada Comment yang cocok)\n\n"
    md += "Daftar di bawah ini adalah ONU yang ada di OLT, tapi bot tidak menemukan nama/comment yang cocok di *Secrets* Mikrotik. Bot mem-fallback menggunakan nama kecil.\n\n"
    md += "| OLT ID | ONU Index | Nama di OLT | Hasil Binding (Fallback) |\n"
    md += "|---|---|---|---|\n"
    
    for row in rows:
        olt_id = row[0]
        onu_idx = row[1]
        name = row[2] or "-"
        fallback = row[3] or "-"
        md += f"| {olt_id} | {onu_idx} | {name} | `{fallback}` |\n"
        
    return md

if __name__ == "__main__":
    report = generate_unbound_report()
    with open(r'C:\BotRedaman\backend\unbound_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print("Report generated.")
