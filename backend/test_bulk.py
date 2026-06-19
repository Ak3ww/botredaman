import sqlite3
import requests

TOKEN = "8773632704:AAFschVyWAyGIwGyjU5mwt1xDlMs3I-NqGc"
CHAT_ID = "298223450"

conn = sqlite3.connect('c:\\BotRedaman\\redaman.db')
cursor = conn.cursor()

criticals = cursor.execute('''
    SELECT al.customer_name, o.name as olt_name, 
           (SELECT rx_power FROM attenuations at WHERE at.onu_id = al.onu_id ORDER BY timestamp DESC LIMIT 1) as rx_power
    FROM alert_states al 
    JOIN olts o ON al.olt_id = o.id 
    WHERE al.status = 'CRITICAL'
    ORDER BY rx_power ASC
''').fetchall()

if criticals:
    msg = f"🔔 <b>[TEST] REMINDER BULK (Tiap 10 Menit)</b> 🔔\n\n"
    msg += "Daftar Pelanggan yang <b>MASIH KRITIS</b>:\n\n"
    for row in criticals:
        name = row[0] or "Tanpa Nama"
        rx = f"{row[2]} dBm" if row[2] is not None else "OFFLINE"
        msg += f"• <b>{name}</b> : {rx}\n"
    msg += "\n<i>Mohon Tim NOC segera melakukan pengecekan!</i>"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    requests.post(url, json=payload)
    print("Pesan Bulk terkirim!")
else:
    # Kirim dummy data jika tidak ada yang kritis
    msg = f"🔔 <b>[TEST] REMINDER BULK (Tiap 10 Menit)</b> 🔔\n\n"
    msg += "Daftar Pelanggan yang <b>MASIH KRITIS</b>:\n\n"
    msg += f"• <b>Bpk Sutarjo</b> : -31.5 dBm\n"
    msg += f"• <b>Siti Hamidah</b> : OFFLINE\n"
    msg += f"• <b>Ucup Surucup</b> : -27.8 dBm\n"
    msg += "\n<i>Mohon Tim NOC segera melakukan pengecekan!</i>"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    requests.post(url, json=payload)
    print("Pesan Bulk Dummy terkirim!")

conn.close()
