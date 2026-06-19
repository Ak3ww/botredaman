import requests

TOKEN = "8773632704:AAFschVyWAyGIwGyjU5mwt1xDlMs3I-NqGc"

commands = [
    {"command": "status", "description": "📊 Lihat ringkasan total OLT & ONU Kritis"},
    {"command": "kritis", "description": "🚨 Tampilkan daftar nama pelanggan dengan redaman buruk"},
    {"command": "cek", "description": "📡 (Spasi Nama/ID) Tarik data LIVE langsung dari OLT"},
    {"command": "cari", "description": "🔍 (Spasi Nama) Cari riwayat pelanggan di Database NOC"},
    {"command": "set_reminder", "description": "⏱ (Spasi Menit) Atur interval pengingat redaman kritis (10/30/60/dll)"}
]

url = f"https://api.telegram.org/bot{TOKEN}/setMyCommands"
response = requests.post(url, json={"commands": commands})

if response.status_code == 200:
    print("Berhasil mengatur Hamburger Menu di Telegram!")
else:
    print("Gagal:", response.text)
