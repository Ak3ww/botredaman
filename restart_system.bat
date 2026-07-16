@echo off
echo Menghentikan semua layanan...
cmd /c "pm2 kill" >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

echo Menunggu 2 detik...
timeout /t 2 /nobreak >nul

echo Memulai backend Node.js (Web Dashboard)...
cd /d C:\BotRedaman\backend
start "Node Dashboard" cmd /k "node server.js"

echo Memulai layanan Collector (SNMP ^& Mikrotik Monitoring)...
start "Python Collector" cmd /k "python collector.py"

echo Memulai Telegram Bot...
start "Telegram Bot" cmd /k "python telegram_bot.py"

echo Semua layanan berhasil dijalankan di window masing-masing!
