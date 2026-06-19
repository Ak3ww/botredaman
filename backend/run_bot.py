import subprocess
import sys
import time

def main():
    print("="*45)
    print("🚀 MEMULAI SISTEM NOC BOT REDAMAN 🚀")
    print("="*45)
    
    # Menjalankan collector.py
    collector = subprocess.Popen([sys.executable, "collector.py"])
    print("✅ Mesin Penyedot Data (Collector) AKTIF.")
    
    # Menjalankan telegram_bot.py
    bot = subprocess.Popen([sys.executable, "telegram_bot.py"])
    print("✅ Telegram Bot AKTIF.")

    # Menjalankan server.js (Node.js)
    web_api = subprocess.Popen(["node", "server.js"])
    print("✅ Web Dashboard Server (Node.js - localhost:8000) AKTIF.")
    
    print("\n[INFO] Seluruh ekosistem NOC kini sedang berjalan bersamaan di terminal ini.")
    print("[INFO] Biarkan terminal ini tetap terbuka.")
    print("[INFO] Tekan 'Ctrl + C' jika ingin mematikan ketiganya.\n")
    
    try:
        # Tahan agar terminal tidak langsung tertutup
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏳ Menerima sinyal berhenti. Mematikan sistem...")
        collector.terminate()
        bot.terminate()
        web_api.terminate()
        print("Sistem berhasil dimatikan dengan aman. Selamat tinggal!")

if __name__ == "__main__":
    main()
