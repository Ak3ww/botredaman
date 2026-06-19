# NOC Bot Redaman & Dashboard 🚀

Sistem pemantau redaman pelanggan (Optical Power RX) dari OLT (HSGQ, VSOL, & GGCLINK). Mengirimkan notifikasi peringatan (*CRITICAL* & *WARNING*) secara real-time ke NOC via Telegram. Dilengkapi Web Dashboard interaktif.

---

## ⚡ Instalasi Sangat Mudah (Plug-and-Play)

Sistem ini didesain agar sangat ramah pemula. Anda **TIDAK PERLU** melakukan pengaturan database atau pemrograman secara manual. Cukup jalankan *Installer Wizard* otomatis yang sudah kami sediakan!

### Langkah 1: Clone Repository ke VPS
Buka terminal VPS Anda (Ubuntu/Debian), lalu jalankan perintah ini untuk mengunduh seluruh sistem:
```bash
git clone https://github.com/Ak3ww/noc-redaman-bot.git
cd noc-redaman-bot
```

### Langkah 2: Jalankan Auto Installer
Di dalam folder tersebut, jalankan file instalasi:
```bash
bash noc-bot-installer.sh
```

**Selesai!** Anda hanya tinggal duduk manis dan menjawab pertanyaan di layar.

---

## 🪄 Apa saja yang ditanyakan oleh Wizard?

Saat *installer* berjalan, layar terminal akan meminta Anda memasukkan data berikut:

1. **Telegram Token & Chat ID**: Digunakan agar bot bisa mengirimkan notifikasi langsung ke grup NOC Anda.
2. **Kredensial Mikrotik (IP Publik/VPN)**: Digunakan agar sistem bisa melacak otomatis ID Pelanggan PPPoE. *Gunakan IP Publik VPS Mikrotik Anda*.
3. **Konfigurasi OLT (Interactive Loop)**: Anda bisa menambahkan OLT satu per satu (contoh: `OLT-Pusat`, IP: `103.X.X.X:161`, Merk: `VSOL`). Jika OLT Anda ada 4, Anda bisa memasukkannya berturut-turut. Jika sudah selesai, cukup kosongkan namanya lalu tekan `ENTER`.

> [!TIP]
> **Otomatisasi Cerdas Berdasarkan Merk!**
> Sistem NOC ini sangat canggih. Jika Anda memasukkan Merk OLT `HSGQ` atau `VSOL`, sistem akan menggunakan protokol **SNMP (UDP 161)**. 
> Namun, jika Anda memasukkan Merk `GGCLINK`, sistem otomatis mengabaikan SNMP dan akan menembak data melalui **Jalur Belakang (HTTP Web API)** berapapun port web-nya (misal: 80, 8001, atau 8002).

---

## ⚙️ Apa yang terjadi di balik layar?

Setelah Anda mengisi *wizard* di atas, script akan bekerja otomatis 100%:
- Menginstal Python, Node.js, dan semua library yang dibutuhkan.
- Membuat database SQLite dan mendaftarkan semua OLT Anda.
- Menjalankan `collector.py` (Mesin Penarik Data) dan `telegram_bot.py` sebagai layanan background (*Systemd*) yang tahan banting (hidup otomatis saat restart).
- Menjalankan Dashboard Web menggunakan `pm2`.
- Membuka port `8000` di Firewall *iptables*.

Di akhir proses, layar akan menampilkan URL cantik untuk mengakses Dashboard Web Anda di browser!

---

## 🛠️ Perintah Pengendalian Layanan di VPS

Semua layanan diatur agar otomatis menyala kembali jika VPS reboot/mati lampu. Jika sewaktu-waktu Anda perlu merestart manual:

### 🖥️ Dashboard Web (PM2)
* **Cek status**: `pm2 status`
* **Restart**: `pm2 restart noc-dashboard`

### 🐍 Backend Engine (Systemd)
* **Cek status Collector**: `sudo systemctl status noc-collector`
* **Cek status Bot Telegram**: `sudo systemctl status noc-telegram-bot`
* **Cek log error**: `cat system.log`
* **Restart services**:
  ```bash
  sudo systemctl restart noc-collector
  sudo systemctl restart noc-telegram-bot
  ```
