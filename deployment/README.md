# Panduan Deployment NOC Bot Redaman (Oracle Cloud Free Tier)

Dokumen ini berisi panduan lengkap langkah-demi-langkah untuk mendeploy sistem **NOC Bot Redaman & Dashboard** ke server **Oracle Cloud Free Tier (Ubuntu VPS)** agar berjalan secara 24/7.

---

## 1. Persiapan VPS di Oracle Cloud Console

1. **Buat Instance Baru**:
   - Masuk ke Oracle Cloud Console.
   - Pilih **Compute** -> **Instances** -> **Create Instance**.
   - Pilih Image: **Canonical Ubuntu 22.04 LTS** atau **24.04 LTS**.
   - Pilih Shape: **Always Free-eligible** (misalnya `VM.Standard.A1.Flex` dengan Ampere CPU atau `VM.Standard.E2.1.Micro` AMD).
   - Unduh/Simpan **SSH Private Key** (`.key` atau `.pub`) untuk login.
   - Buat Instance.

2. **Buka Port di Oracle Virtual Cloud Network (VCN)**:
   - Pada halaman detail instance Anda, klik **Primary VNIC** -> **Subnet**.
   - Klik **Security Lists** (biasanya bernama *Default Security List for...*).
   - Klik **Add Ingress Rules** untuk membuka port dashboard web:
     - **Source CIDR**: `0.0.0.0/0`
     - **IP Protocol**: `TCP`
     - **Destination Port Range**: `8000`
     - **Description**: `NOC Dashboard Web API`
   - Klik **Add Ingress Rules**.

---

## 2. Struktur Folder Deployment Lokal

Di komputer kantor Anda, folder `C:\BotRedaman\deployment` saat ini sudah dipaketkan dengan rapi:
```text
C:\BotRedaman\deployment\
├── dist\                  # Aset frontend React terkompilasi
├── collector.py           # Engine penarik data SNMP & Alerting
├── telegram_bot.py        # Telegram Bot Command Handler
├── server.js              # Node.js API Server
├── database.py            # SQLite helper
├── package.json           # Dependensi Node.js
├── requirements.txt       # Dependensi Python
└── config.json            # Konfigurasi token & URL
```

---

## 3. Upload File ke VPS Oracle

Gunakan aplikasi SFTP (seperti **FileZilla** atau **WinSCP**) atau gunakan perintah terminal `scp` untuk meng-upload seluruh isi folder `C:\BotRedaman\deployment` ke folder `/home/ubuntu/noc-bot` di VPS Anda.

**Contoh perintah SCP dari lokal:**
```powershell
# Jalankan di terminal komputer lokal Anda
scp -i path_to_ssh_key.key -r C:\BotRedaman\deployment\* ubuntu@IP_PUBLIC_VPS_ORACLE:/home/ubuntu/noc-bot
```
*(Direkomendasikan: Upload juga file database `redaman.db` dari komputer kantor Anda ke folder `/home/ubuntu/noc-bot` agar riwayat data, OLT IP, dan cache nama pelanggan tidak hilang).*

---

## 4. Cara Instalasi Otomatis via `install.sh` (1 Command)

Masuk ke VPS Anda via SSH:
```bash
ssh -i path_to_ssh_key.key ubuntu@IP_PUBLIC_VPS_ORACLE
```

Masuk ke folder hasil upload/git clone, beri izin eksekusi pada script, dan jalankan:
```bash
cd /home/ubuntu/noc-bot
chmod +x install.sh
./install.sh
```

### 💡 Apa saja yang dilakukan secara otomatis oleh `install.sh`?
1. **Deteksi IP Publik VPS**: Mendeteksi IP publik eksternal VPS secara otomatis untuk konfigurasi dashboard URL.
2. **Pemasangan Dependensi**: Menginstal Python3, Virtualenv, SQLite3, dan Node.js v20 secara otomatis.
3. **Setup Lingkungan Virtual**: Membuat virtual environment Python, mengupdate pip, dan menginstal dependensi (`pysnmp` & `requests`).
4. **Interactive Token Setup**: Menanyakan token Bot Telegram, Chat ID, dan URL Dashboard secara interaktif (dengan default yang dapat langsung dipilih menggunakan tombol `Enter`).
5. **Firewall Port 8000**: Membuka blokir port masuk `8000` di iptables lokal Ubuntu secara permanen.
6. **systemd Daemon Service**: Membuat service `noc-collector.service` dan `noc-telegram-bot.service` secara otomatis, meregistrasikannya ke sistem, dan langsung menjalankannya.
7. **PM2 Process Manager**: Menginstal PM2 secara global, meregistrasikan `server.js` (dashboard), dan mengaturnya agar menyala otomatis saat server reboot.

---

## 5. Perintah Pengendalian Layanan di VPS

Setelah instalasi selesai, Anda dapat memantau dan mengendalikan layanan menggunakan perintah berikut:

### Dashboard Web (PM2)
```bash
# Melihat daftar proses PM2 yang berjalan
pm2 status

# Melihat log langsung dari dashboard
pm2 logs noc-dashboard

# Restart / Stop Dashboard
pm2 restart noc-dashboard
pm2 stop noc-dashboard
```

### Python Engine (Collector & Telegram Bot)
```bash
# Cek status berjalan
sudo systemctl status noc-collector
sudo systemctl status noc-telegram-bot

# Melihat live logs / logs ter-buffer dari Collector
sudo journalctl -u noc-collector -f --no-tail

# Restart Collector / Telegram Bot
sudo systemctl restart noc-collector
sudo systemctl restart noc-telegram-bot
```

---

## 6. Verifikasi Akhir
Buka browser Anda dan akses:
`http://IP_VPS_ORACLE_ANDA:8000`

Dashboard Anda kini ter-deploy secara pro, responsif, dan berjalan 24/7 gratis selamanya!
Jika bot di Telegram merespons perintah `/status` atau `/kritis`, maka seluruh sistem backend juga telah aktif dan terintegrasi penuh.
