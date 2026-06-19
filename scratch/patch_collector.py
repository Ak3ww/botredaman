import re

file_path = r"C:\BotRedaman\backend\collector.py"

# Try different encodings to load the file
content = None
for enc in ["utf-8", "cp1252", "latin-1"]:
    try:
        with open(file_path, "r", encoding=enc) as f:
            content = f.read()
        print(f"Loaded file successfully with encoding: {enc}")
        break
    except Exception as e:
        print(f"Failed loading with encoding {enc}")

if content is None:
    raise Exception("Could not load collector.py with any known encoding.")

# 1. Define new process_alert_state implementation
new_process_alert_state = """def process_alert_state(cursor, olt_id, olt_name, onu_id, customer, rx_power, offline_reason=None,
                        is_currently_offline=False, last_up_time=None, last_down_time=None, alive_time=None):
    \"\"\"
    State machine yang mengelola notifikasi Telegram berdasarkan perubahan status ONU.

    Alur:
    1. Ambil status lama dari alert_states (key: onu_id + olt_id)
    2. Hitung status baru berdasarkan rx_power + hysteresis + online state
    3. Jika status berubah: kirim notif + update DB
    4. Jika status sama: update customer_name, registration info, alive time, JANGAN update last_alert_time
    \"\"\"
    now     = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    bar     = rx_bar(rx_power)

    # Ambil state lama — key composite (onu_id, olt_id)
    state_row = cursor.execute(
        'SELECT status, last_alert_time, last_offline_reason, last_up_time, last_down_time, alive_time FROM alert_states WHERE onu_id = ? AND olt_id = ?',
        (onu_id, olt_id)
    ).fetchone()

    old_status = state_row[0] if state_row else None
    new_status = get_dbm_status(rx_power, current_status=old_status or 'NORMAL', is_currently_offline=is_currently_offline)

    # ── Cooldown check ────────────────────────────────────────────────────────
    secs_since = 9999
    if state_row and state_row[1]:
        try:
            last_dt = datetime.datetime.strptime(state_row[1], "%Y-%m-%d %H:%M:%S")
            secs_since = (now - last_dt).total_seconds()
        except:
            pass

    status_changed = (old_status != new_status)

    # ── Jika belum ada di DB: INSERT baru ─────────────────────────────────────
    if state_row is None:
        # Kirim notif hanya jika tidak NORMAL (tidak notif saat pertama kali boot)
        if new_status == 'WARNING':
            send_telegram(
                f"⚠️ <b>ALERT: REDAMAN WARNING</b> ⚠️\\n{chr(8212)*28}\\n"
                f"🖥 OLT    : <b>{olt_name}</b>\\n"
                f"👤 Nama   : <b>{customer}</b>\\n"
                f"📉 Redaman: {bar}\\n"
                f"Alive Time: <b>{alive_time or '-'}</b>\\n{chr(8212)*28}\\n"
                f"<i>💡 Sinyal mulai memburuk, mohon dipantau.</i>",
                reply_markup={"inline_keyboard": [[{"text": "🖥 Detail (Web)", "url": f"{DASHBOARD_URL}/?onu_id={onu_id}"}]]}
            )
        elif new_status == 'CRITICAL':
            send_telegram(
                f"🚨 <b>ALERT: REDAMAN KRITIS!</b> 🚨\\n{chr(8212)*28}\\n"
                f"🖥 OLT    : <b>{olt_name}</b>\\n"
                f"👤 Nama   : <b>{customer}</b>\\n"
                f"📉 Redaman: {bar}\\n"
                f"Alive Time: <b>{alive_time or '-'}</b>\\n{chr(8212)*28}\\n"
                f"<i>⚠️ Segera lakukan pengecekan!</i>",
                reply_markup={"inline_keyboard": [[{"text": "🖥 Detail (Web)", "url": f"{DASHBOARD_URL}/?onu_id={onu_id}"}]]}
            )
        elif new_status == 'OFFLINE':
            send_telegram(
                f"🔌 <b>ALERT: ONU OFFLINE!</b> 🔌\\n{chr(8212)*28}\\n"
                f"🖥 OLT    : <b>{olt_name}</b>\\n"
                f"👤 Nama   : <b>{customer}</b>\\n"
                f"🔍 Alasan : <b>{offline_reason or 'Unknown'}</b>\\n"
                f"Last Down: <b>{last_down_time or '-'}</b>\\n{chr(8212)*28}\\n"
                f"<i>⚠️ Cek kelistrikan atau kabel pelanggan!</i>",
                reply_markup={"inline_keyboard": [[{"text": "🖥 Detail (Web)", "url": f"{DASHBOARD_URL}/?onu_id={onu_id}"}]]}
            )
        cursor.execute(
            'INSERT OR IGNORE INTO alert_states (onu_id, olt_id, customer_name, status, last_alert_time, last_offline_reason, last_up_time, last_down_time, alive_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (onu_id, olt_id, customer, new_status, now_str, offline_reason if new_status == 'OFFLINE' else None, last_up_time, last_down_time, alive_time)
        )
        return

    # ── Status tidak berubah: update nama/reason/times, JANGAN sentuh last_alert_time ──
    if not status_changed:
        updated_reason = offline_reason if new_status == 'OFFLINE' else state_row[2]
        cursor.execute(
            'UPDATE alert_states SET customer_name = ?, last_offline_reason = ?, last_up_time = ?, last_down_time = ?, alive_time = ? WHERE onu_id = ? AND olt_id = ?',
            (customer, updated_reason, last_up_time or state_row[3], last_down_time or state_row[4], alive_time or state_row[5], onu_id, olt_id)
        )
        return

    # ── Status BERUBAH: kirim notif (dengan cooldown) + update DB ────────────
    msg = None

    if new_status == 'NORMAL':
        # Recovery — selalu kirim tanpa cooldown (penting bagi NOC)
        msg = (
            f"✅ <b>RECOVERED — KEMBALI NORMAL</b> ✅\\n{chr(8212)*28}\\n"
            f"🖥 OLT    : <b>{olt_name}</b>\\n"
            f"👤 Nama   : <b>{customer}</b>\\n"
            f"📉 Redaman: {bar}\\n"
            f"Alive Time: <b>{alive_time or '-'}</b>\\n"
            f"Last Up   : <b>{last_up_time or '-'}</b>\\n{chr(8212)*28}\\n"
            f"<i>🎉 Sinyal kembali bagus!</i>"
        )

    elif new_status == 'OFFLINE' and old_status != 'OFFLINE':
        msg = (
            f"🔌 <b>ALERT: ONU OFFLINE!</b> 🔌\\n{chr(8212)*28}\\n"
            f"Status   : {old_status} ➡️ ⚫ <b>OFFLINE</b>\\n"
            f"🖥 OLT    : <b>{olt_name}</b>\\n"
            f"👤 Nama   : <b>{customer}</b>\\n"
            f"🔍 Alasan : <b>{offline_reason or 'Unknown'}</b>\\n"
            f"Last Down: <b>{last_down_time or '-'}</b>\\n{chr(8212)*28}\\n"
            f"<i>⚠️ Cek kelistrikan atau kabel pelanggan!</i>"
        )

    elif old_status == 'OFFLINE' and new_status != 'OFFLINE':
        # Kembali online setelah offline
        msg = (
            f"✅ <b>ONU KEMBALI ONLINE</b> ✅\\n{chr(8212)*28}\\n"
            f"Status   : ⚫ OFFLINE ➡️ <b>{new_status}</b>\\n"
            f"🖥 OLT    : <b>{olt_name}</b>\\n"
            f"👤 Nama   : <b>{customer}</b>\\n"
            f"📉 Redaman: {bar}\\n"
            f"Alive Time: <b>{alive_time or '-'}</b>\\n"
            f"Last Up   : <b>{last_up_time or '-'}</b>\\n{chr(8212)*28}\\n"
            f"<i>Pelanggan kembali terhubung.</i>"
        )

    elif old_status == 'NORMAL' and new_status == 'WARNING':
        if secs_since >= COOLDOWN_SECS:
            msg = (
                f"⚠️ <b>ALERT: REDAMAN TURUN (WARNING)</b> ⚠️\\n{chr(8212)*28}\\n"
                f"🖥 OLT    : <b>{olt_name}</b>\\n"
                f"👤 Nama   : <b>{customer}</b>\\n"
                f"📉 Redaman: {bar}\\n"
                f"Alive Time: <b>{alive_time or '-'}</b>\\n{chr(8212)*28}\\n"
                f"<i>💡 Redaman melewati -23.0 dBm</i>"
            )

    elif old_status == 'NORMAL' and new_status == 'CRITICAL':
        if secs_since >= COOLDOWN_SECS:
            msg = (
                f"🚨 <b>ALERT: REDAMAN DROP PARAH!</b> 🚨\\n{chr(8212)*28}\\n"
                f"🖥 OLT    : <b>{olt_name}</b>\\n"
                f"👤 Nama   : <b>{customer}</b>\\n"
                f"📉 Redaman: {bar}\\n"
                f"Alive Time: <b>{alive_time or '-'}</b>\\n{chr(8212)*28}\\n"
                f"<i>⚠️ Redaman anjlok ke bawah -26.0 dBm!</i>"
            )

    elif old_status == 'WARNING' and new_status == 'CRITICAL':
        if secs_since >= COOLDOWN_SECS:
            msg = (
                f"🚨 <b>ALERT: REDAMAN SEMAKIN PARAH!</b> 🚨\\n{chr(8212)*28}\\n"
                f"Status   : 🟡 WARNING ➡️ 🔴 <b>CRITICAL</b>\\n"
                f"🖥 OLT    : <b>{olt_name}</b>\\n"
                f"👤 Nama   : <b>{customer}</b>\\n"
                f"📉 Redaman: {bar}\\n"
                f"Alive Time: <b>{alive_time or '-'}</b>\\n{chr(8212)*28}\\n"
                f"<i>⚠️ Memburuk melewati batas kritis -26.0 dBm!</i>"
            )

    elif old_status == 'CRITICAL' and new_status == 'WARNING':
        if secs_since >= COOLDOWN_SECS:
            msg = (
                f"🟡 <b>IMPROVED: SINYAL MEMBAIK</b> 🟡\\n{chr(8212)*28}\\n"
                f"Status   : 🔴 CRITICAL ➡️ 🟡 <b>WARNING</b>\\n"
                f"🖥 OLT    : <b>{olt_name}</b>\\n"
                f"👤 Nama   : <b>{customer}</b>\\n"
                f"📉 Redaman: {bar}\\n"
                f"Alive Time: <b>{alive_time or '-'}</b>\\n{chr(8212)*28}\\n"
                f"<i>👍 Perbaikan terdeteksi, belum sepenuhnya normal.</i>"
            )

    if msg:
        send_telegram(msg, reply_markup={"inline_keyboard": [[
            {"text": "🖥 Detail (Web)", "url": f"{DASHBOARD_URL}/?onu_id={onu_id}"}
        ]]})

    # Update DB
    cursor.execute('''
        UPDATE alert_states 
        SET status=?, last_alert_time=?, customer_name=?, last_offline_reason=?, last_up_time=?, last_down_time=?, alive_time=? 
        WHERE onu_id=? AND olt_id=?
    ''', (new_status, now_str, customer, offline_reason, last_up_time, last_down_time, alive_time, onu_id, olt_id))"""

# 2. Define new pull_data_and_alert implementation
new_pull_data_and_alert = """def pull_data_and_alert():
    print(f"\\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Memulai penarikan data SNMP...")
    conn   = get_conn()
    cursor = conn.cursor()
    ensure_schema(conn)

    olts = cursor.execute('SELECT id, name, ip_port, brand, community FROM olts').fetchall()

    for olt_id, olt_name, ip_port, olt_brand, community in olts:
        if olt_brand not in OIDS:
            print(f"  Skip {olt_name}: Brand '{olt_brand}' tidak dikenal.")
            continue

        cfg = OIDS[olt_brand]
        if not cfg.get("rx"):
            print(f"  Skip {olt_name}: OID rx belum diset.")
            continue

        ip, port = ip_port.rsplit(':', 1)
        port = int(port)

        # ── Sync cache nama/SN/firmware (hanya jika perlu) ───────────────────
        if needs_cache_sync(cursor, olt_id):
            sync_olt_name_cache(cursor, olt_id, ip, port, community, cfg)
            conn.commit()

        # ── Tarik rx_power LANGSUNG dari OLT (real-time, bukan cache) ────────
        rx_data = get_snmp_walk(ip, port, community, cfg["rx"], version=cfg["vsnmp"])
        
        # Tarik data status, registrasi, alive time, dan alasan offline
        up_time_data = get_snmp_walk(ip, port, community, cfg["uptime"], version=cfg["vsnmp"])
        down_time_data = get_snmp_walk(ip, port, community, cfg["downtime"], version=cfg["vsnmp"])
        offline_data = get_snmp_walk(ip, port, community, cfg["offline"], version=cfg["vsnmp"])
        alive_data = get_snmp_walk(ip, port, community, cfg["alive"], version=cfg["vsnmp"])
        
        status_data = {}
        if olt_brand == "HSGQ":
            status_data = get_snmp_walk(ip, port, community, cfg["status"], version=cfg["vsnmp"])

        # Jika data fundamental (uptime / rx) gagal ditarik sama sekali, skip OLT ini di siklus ini
        if not rx_data and not up_time_data:
            print(f"  ⚠️  Gagal menarik data dari {olt_name}. Siklus ini dilewati.")
            continue

        print(f"  [{olt_name}] Data diterima dari SNMP.")

        # ── Ambil semua ONU dari cache sebagai daftar master ─────────────────
        cached = cursor.execute(
            'SELECT onu_id, customer_name FROM onu_name_cache WHERE olt_id = ?', (olt_id,)
        ).fetchall()
        all_onus = {r[0]: r[1] for r in cached}

        # Gabungkan semua ONU index yang terdeteksi di cycle ini
        all_detected_indices = set(rx_data.keys()) | set(up_time_data.keys())
        if status_data:
            all_detected_indices.update(status_data.keys())

        # ONU baru yang belum di cache — GET langsung
        for onu_idx in all_detected_indices:
            if onu_idx not in all_onus:
                name_val = get_snmp_get(ip, port, community, f"{cfg['name']}.{onu_idx}", version=cfg["vsnmp"])
                sn_val   = get_snmp_get(ip, port, community, f"{cfg['sn']}.{onu_idx}",   version=cfg["vsnmp"])
                ver_val  = get_snmp_get(ip, port, community, f"{cfg['version']}.{onu_idx}", version=cfg["vsnmp"])
                customer = (name_val or f"ONU-{onu_idx}").strip()
                cursor.execute(
                    'INSERT OR REPLACE INTO onu_name_cache (onu_id, olt_id, customer_name, sn, firmware_version, last_updated) VALUES (?,?,?,?,?,?)',
                    (onu_idx, olt_id, customer, sn_val or "", ver_val or "", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                all_onus[onu_idx] = customer

        # ── Proses setiap ONU ─────────────────────────────────────────────────
        for onu_idx, customer in all_onus.items():
            try:
                raw_rx = rx_data.get(onu_idx)
                dbm    = normalize_dbm(raw_rx, rx_scale=cfg.get("rx_scale", 100.0))

                # Ambil metrik diagnostik
                last_up = up_time_data.get(onu_idx)
                last_down = down_time_data.get(onu_idx)
                alive = alive_data.get(onu_idx)
                reason = offline_data.get(onu_idx)

                # Bersihkan string atau berikan default
                if last_up: last_up = last_up.strip()
                if last_down: last_down = last_down.strip()
                if alive: alive = alive.strip()
                if reason: reason = reason.strip()

                # Tentukan online/offline status secara akurat
                is_currently_offline = False
                if olt_brand == "HSGQ":
                    status_val = status_data.get(onu_idx)
                    if status_val is not None:
                        is_currently_offline = (status_val.strip() != '1')
                    else:
                        is_currently_offline = (dbm is None)
                    # Format alive time
                    if alive and alive != "0":
                        alive = format_hsgq_alive(alive)
                    else:
                        alive = "-"
                elif olt_brand == "VSOL":
                    if last_up and last_down and last_up != "N/A" and last_down != "N/A":
                        is_currently_offline = (last_down > last_up)
                    elif last_up == "N/A" or alive in ("0", "00:00:00", "0 00:00:00"):
                        is_currently_offline = True
                    else:
                        is_currently_offline = (dbm is None)

                # Jika offline, gunakan reason OID. Jika online, set reason ke None atau simpan historis
                if is_currently_offline:
                    offline_reason = reason or "Unknown"
                    dbm = None
                else:
                    offline_reason = None

                # Simpan ke history attenuations (data real-time, BUKAN cache)
                cursor.execute(
                    'INSERT INTO attenuations (olt_id, port_name, onu_id, rx_power, timestamp) VALUES (?,?,?,?,datetime("now","localtime"))',
                    (olt_id, "GPON", onu_idx, dbm)
                )

                # Proses alerting
                process_alert_state(
                    cursor=cursor,
                    olt_id=olt_id,
                    olt_name=olt_name,
                    onu_id=onu_idx,
                    customer=customer,
                    rx_power=dbm,
                    offline_reason=offline_reason,
                    is_currently_offline=is_currently_offline,
                    last_up_time=last_up,
                    last_down_time=last_down,
                    alive_time=alive
                )

            except Exception as e:
                print(f"  [Error] ONU {onu_idx}: {e}")

        conn.commit()

    # ── Bulk reminder ─────────────────────────────────────────────────────────
    check_and_send_bulk_reminder(cursor)

    # ── Pruning data lama (1x per hari cukup, tapi cek tiap siklus — cepat) ──
    prune_old_attenuations(conn)

    conn.close()
    print(f"  Selesai.\\n")"""

# Replace process_alert_state in file content
start_marker = "def process_alert_state(cursor, olt_id, olt_name, onu_id, customer, rx_power, offline_reason=None):"
end_marker = "# ── Bulk Reminder ──"

idx_start = content.find(start_marker)
idx_end = content.find(end_marker)

if idx_start != -1 and idx_end != -1:
    content = content[:idx_start] + new_process_alert_state + "\n\n" + content[idx_end:]
    print("process_alert_state replaced in memory.")
else:
    print("Failed to locate process_alert_state markers.")

# Replace pull_data_and_alert in file content
start_marker_pull = "def pull_data_and_alert():"
end_marker_pull = "# ── Entry Point ──"

idx_start_pull = content.find(start_marker_pull)
idx_end_pull = content.find(end_marker_pull)

if idx_start_pull != -1 and idx_end_pull != -1:
    content = content[:idx_start_pull] + new_pull_data_and_alert + "\n\n" + content[idx_end_pull:]
    print("pull_data_and_alert replaced in memory.")
else:
    print("Failed to locate pull_data_and_alert markers.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("File successfully saved as clean UTF-8!")
