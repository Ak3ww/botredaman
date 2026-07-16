import subprocess
import time
import sys
import os
import signal

def start_all():
    print("Memulai Sistem Bot Redaman Noc...")
    os.chdir(r"C:\BotRedaman\backend")
    
    # Matikan service sebelumnya yang mungkin nyangkut
    subprocess.run("taskkill /F /IM node.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Jangan matikan python.exe karena script ini adalah python.exe!
    
    processes = []
    
    try:
        print("-> Menyalakan Web Dashboard (Node.js)...")
        p1 = subprocess.Popen(["node", "server.js"], shell=True)
        processes.append(p1)
        
        print("-> Menyalakan SNMP Collector...")
        p2 = subprocess.Popen(["python", "collector.py"], shell=True)
        processes.append(p2)
        
        print("-> Menyalakan Telegram Bot...")
        p3 = subprocess.Popen(["python", "telegram_bot.py"], shell=True)
        processes.append(p3)
        
        print("Sistem berjalan! JANGAN TUTUP JENDELA INI.")
        print("Dashboard: http://localhost:8000")
        
        # Keep alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nMematikan semua sistem...")
        for p in processes:
            p.terminate()
        print("Sistem dihentikan.")
        sys.exit(0)

if __name__ == "__main__":
    start_all()
