const express = require('express');
const cors    = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path    = require('path');

const app    = express();
const PORT   = process.env.PORT || 8000;
const DB_FILE = path.join(__dirname, 'redaman.db');

app.use(cors());
app.use(express.json());

// Serve static assets dari Vite React production build
const distPath = path.join(__dirname, 'dist');
app.use(express.static(distPath));

// Buka DB dalam mode READ-ONLY + WAL-compatible
const db = new sqlite3.Database(DB_FILE, sqlite3.OPEN_READWRITE, (err) => {
    if (err) {
        console.error('Error membuka database:', err.message);
    } else {
        // Aktifkan WAL mode agar bisa baca bersamaan saat Python write
        db.run("PRAGMA journal_mode=WAL");
        db.run("PRAGMA synchronous=NORMAL");
        console.log(`✅ DB terhubung: ${DB_FILE}`);
    }
});

// ── GET /api/olts ─────────────────────────────────────────────────────────
app.get('/api/olts', (req, res) => {
    db.all('SELECT * FROM olts', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// ── GET /api/attenuations ─────────────────────────────────────────────────
// Mengembalikan data TERBARU per (olt_id, onu_id).
// Data real-time diambil dari attenuations (history).
// Data statis (SN, firmware, nama) di-JOIN dari onu_name_cache.
// Status & offline_reason di-JOIN dari alert_states.
app.get('/api/attenuations', (req, res) => {
    db.all(`
        SELECT
            o.id            AS olt_id,
            o.name          AS olt_name,
            o.brand,
            a.onu_id,
            a.port_name,
            a.rx_power,
            a.tx_power,
            a.timestamp,
            -- Nama pelanggan: dari cache (lebih akurat)
            COALESCE(c.customer_name, a.onu_id) AS customer_name,
            -- Data statis dari cache
            c.sn,
            c.firmware_version,
            -- Status dan alasan offline dari alert_states
            s.status              AS alert_status,
            s.last_offline_reason,
            s.last_alert_time,
            s.last_up_time,
            s.last_down_time,
            s.alive_time
        FROM attenuations a
        JOIN olts o ON a.olt_id = o.id
        LEFT JOIN onu_name_cache c ON a.onu_id = c.onu_id AND a.olt_id = c.olt_id
        LEFT JOIN alert_states   s ON a.onu_id = s.onu_id AND a.olt_id = s.olt_id
        WHERE a.id IN (
            SELECT MAX(id)
            FROM attenuations
            GROUP BY olt_id, onu_id
        )
        ORDER BY
            CASE COALESCE(s.status,'NORMAL')
                WHEN 'OFFLINE'  THEN 0
                WHEN 'CRITICAL' THEN 1
                WHEN 'WARNING'  THEN 2
                ELSE 3
            END,
            a.rx_power ASC NULLS FIRST
    `, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// ── GET /api/chart_data?onu_id=X&olt_id=Y ────────────────────────────────
// Mengembalikan 60 data historis TERBARU, diurutkan ASC untuk grafik.
app.get('/api/chart_data', (req, res) => {
    const { onu_id, olt_id } = req.query;
    if (!onu_id) return res.status(400).json({ error: 'onu_id diperlukan' });

    let sql, params;
    if (olt_id) {
        // Filter by olt_id juga untuk hindari ambigu antar OLT
        sql    = `SELECT rx_power, timestamp FROM (
                    SELECT rx_power, timestamp FROM attenuations
                    WHERE onu_id = ? AND olt_id = ?
                    ORDER BY timestamp DESC LIMIT 60
                  ) ORDER BY timestamp ASC`;
        params = [onu_id, olt_id];
    } else {
        sql    = `SELECT rx_power, timestamp FROM (
                    SELECT rx_power, timestamp FROM attenuations
                    WHERE onu_id = ?
                    ORDER BY timestamp DESC LIMIT 60
                  ) ORDER BY timestamp ASC`;
        params = [onu_id];
    }

    db.all(sql, params, (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// ── GET /api/status_summary ────────────────────────────────────────────────
// Statistik cepat: jumlah ONU per status untuk dashboard header
app.get('/api/status_summary', (req, res) => {
    db.all(`
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'OFFLINE'  THEN 1 ELSE 0 END) as offline,
            SUM(CASE WHEN status = 'CRITICAL' THEN 1 ELSE 0 END) as critical,
            SUM(CASE WHEN status = 'WARNING'  THEN 1 ELSE 0 END) as warning,
            SUM(CASE WHEN status = 'NORMAL'   THEN 1 ELSE 0 END) as normal
        FROM alert_states
    `, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows[0] || { total: 0, offline: 0, critical: 0, warning: 0, normal: 0 });
    });
});

// ── GET /api/onu_detail?onu_id=X&olt_id=Y ─────────────────────────────────
// Detail lengkap satu ONU: SN, firmware, status, rx terbaru
app.get('/api/onu_detail', (req, res) => {
    const { onu_id, olt_id } = req.query;
    if (!onu_id || !olt_id) return res.status(400).json({ error: 'onu_id dan olt_id diperlukan' });

    db.get(`
        SELECT
            c.customer_name, c.sn, c.firmware_version,
            s.status, s.last_offline_reason, s.last_alert_time,
            s.last_up_time, s.last_down_time, s.alive_time,
            (SELECT rx_power FROM attenuations WHERE onu_id=? AND olt_id=? ORDER BY timestamp DESC LIMIT 1) as rx_power,
            (SELECT timestamp FROM attenuations WHERE onu_id=? AND olt_id=? ORDER BY timestamp DESC LIMIT 1) as last_seen
        FROM onu_name_cache c
        LEFT JOIN alert_states s ON c.onu_id = s.onu_id AND c.olt_id = s.olt_id
        WHERE c.onu_id = ? AND c.olt_id = ?
    `, [onu_id, olt_id, onu_id, olt_id, onu_id, olt_id], (err, row) => {
        if (err) return res.status(500).json({ error: err.message });
        if (!row) return res.status(404).json({ error: 'ONU tidak ditemukan' });
        res.json(row);
    });
});

// ── SPA fallback ───────────────────────────────────────────────────────────
app.get('*any', (req, res) => {
    res.sendFile(path.join(distPath, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Dashboard server berjalan di http://0.0.0.0:${PORT}`);
});
