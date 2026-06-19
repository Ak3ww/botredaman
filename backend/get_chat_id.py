import requests
import sys

TOKEN = "8773632704:AAFschVyWAyGIwGyjU5mwt1xDlMs3I-NqGc"
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

try:
    response = requests.get(URL)
    data = response.json()
    
    if data["ok"]:
        results = data["result"]
        if len(results) > 0:
            # Mengambil chat ID dari pesan terakhir
            chat_id = results[-1]["message"]["chat"]["id"]
            username = results[-1]["message"]["chat"].get("first_name", "User")
            print(f"BERHASIL! Chat ID untuk {username} adalah: {chat_id}")
        else:
            print("GAGAL: Belum ada pesan masuk. Pastikan Anda sudah mengklik tombol START di bot Telegram Anda!")
    else:
        print(f"Error dari Telegram API: {data.get('description')}")
except Exception as e:
    print(f"Terjadi kesalahan: {e}")
