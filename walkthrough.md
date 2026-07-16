# Fitur `/olt` & Fix Bulk Reminder

## Apa yang telah dilakukan?
1. **Fix Notifikasi Reminder Tanpa Redaman**:
   - **Akar Masalah**: Saat ONU menjadi kritis, kadang terjadi *packet loss* yang membuat OLT mengirim `NULL` untuk redamannya. Karena query sebelumnya mengambil data historis paling baru secara mutlak, nilai `NULL` inilah yang terbaca sehingga bot mencetak "None dBm" di notifikasi Bulk Reminder Telegram.
   - **Solusi**: Saya telah merombak kueri SQL di dalam `check_and_send_bulk_reminder` sehingga bot akan mengabaikan nilai `NULL` dan secara proaktif mencari *nilai angka desimal (dBm) aktual terakhir* yang berhasil terekam di database sebelum *packet loss* terjadi. Kini reminder di Telegram akan selalu menampilkan nominal redaman secara akurat.

2. **Perintah Telegram `/olt`**:
   - Saya telah menyuntikkan *command handler* baru bernama `/olt` ke dalam `telegram_bot.py`.
   - **Fitur Auto-Tips**: Jika Bapak hanya mengetik `/olt` saja tanpa embel-embel, bot akan ramah memberikan tips (contoh: `/olt vsol`).
   - **Fitur Live Listing**: Jika Bapak mengetik `/olt vsol`, bot akan menarik nama-nama pelanggan di V-SOL langsung dari *database* beserta **indikator redaman terakhir mereka**. Status diurutkan secara cerdas: Kritis di atas, lalu Warning, lalu Normal, lalu Offline di bawah.
   - **Dashboard Integration**: Di bagian bawah pesan balasan `/olt`, tersedia tombol "🖥 Buka Dashboard" yang akan membawa Bapak langsung ke halaman web yang telah ter-*filter* khusus untuk OLT tersebut.

## Status
✅ Beroperasi penuh. Bot tidak dimatikan sama sekali selama injeksi kode berlangsung, semua berjalan secara *autonomous* di belakang layar.
