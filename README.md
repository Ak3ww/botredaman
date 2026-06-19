# NOC Bot Redaman & Dashboard - Standalone Installer

Sistem ini memantau redaman pelanggan (Optical Power RX) dari OLT GPON/EPON (HSGQ & VSOL) dan mengirimkan notifikasi peringatan secara real-time ke NOC via Telegram. Dilengkapi juga dengan Web Dashboard interaktif.

Untuk mempermudah proses deployment ke **Oracle Cloud Free Tier (Ubuntu VPS)** agar berjalan 24/7 secara gratis, kami telah membuat paket **Standalone Auto Installer** bernama `noc-bot-installer.sh`.

---

## ⚡ Deployment Cepat (1 atau 2 Command)

Anda hanya memerlukan file **`noc-bot-installer.sh`** untuk di-upload ke VPS Anda. File ini berukuran sangat kecil (~290 KB) karena di dalamnya sudah terkompresi dan ter-encode seluruh kode program backend (Python), frontend (React HTML/JS/CSS), dan file konfigurasi.

### Langkah 1: Transfer Installer ke VPS
Upload file `noc-bot-installer.sh` ke VPS Anda menggunakan SFTP (FileZilla/WinSCP) atau melalui perintah SCP:
```bash
scp -i path_to_key.key noc-bot-installer.sh ubuntu@IP_PUBLIC_VPS:/home/ubuntu/
```

### Langkah 2: Jalankan Installer
Masuk ke VPS via SSH, berikan izin eksekusi, dan jalankan script:
```bash
ssh -i path_to_key.key ubuntu@IP_PUBLIC_VPS
chmod +x noc-bot-installer.sh
./noc-bot-installer.sh
```

**Selesai!** Script akan mendeteksi IP publik secara otomatis, meminta input token Telegram bot, membuat database SQLite, mendaftarkan layanan background (systemd untuk bot & collector), memasang PM2, serta langsung menyalakan dashboard web di port `8000`.

---

## 📂 Mengimpor Database Lama (Opsional - Sangat Direkomendasikan)
Agar riwayat grafik redaman, konfigurasi custom, dan cache nama pelanggan tidak hilang dari server lokal:
1. Matikan sementara service collector di VPS:
   ```bash
   sudo systemctl stop noc-collector
   ```
2. Upload file database lokal Anda (`C:\BotRedaman\backend\redaman.db`) ke folder instalasi di VPS (misalnya `/home/ubuntu/redaman.db`).
3. Jalankan kembali service collector:
   ```bash
   sudo systemctl start noc-collector
   ```

---

## 🛠️ Perintah Pengendalian Layanan di VPS

Semua layanan diatur menggunakan systemd dan PM2 agar secara otomatis menyala kembali jika VPS reboot.

### 🖥️ Dashboard Web (PM2)
* **Cek status dashboard**: `pm2 status`
* **Melihat log dashboard**: `pm2 logs noc-dashboard`
* **Restart dashboard**: `pm2 restart noc-dashboard`

### 🐍 Backend Engine (Collector & Telegram Bot - Systemd)
* **Cek status Collector**: `sudo systemctl status noc-collector`
* **Cek status Bot Telegram**: `sudo systemctl status noc-telegram-bot`
* **Melihat log real-time Collector**: `sudo journalctl -u noc-collector -f`
* **Melihat log real-time Bot Telegram**: `sudo journalctl -u noc-telegram-bot -f`
* **Restart services**:
  ```bash
  sudo systemctl restart noc-collector
  sudo systemctl restart noc-telegram-bot
  ```

---

## 🔒 Catatan Keamanan & Firewall
1. **Oracle Cloud VCN**: Pastikan Anda membuka port masuk **`8000`** di Security List Virtual Cloud Network (VCN) Oracle Cloud.
2. **SNMP Access Control**: Jika OLT VSOL berada di jaringan lokal komputer kantor (`192.168.30.6`), lakukan *port forwarding* port SNMP `161` (UDP) di router kantor agar VPS dapat menjangkaunya lewat IP publik kantor Anda. Batasi akses pengiriman data UDP port 161 di router kantor hanya menerima request dari IP Publik VPS Oracle Anda untuk keamanan maksimal.
