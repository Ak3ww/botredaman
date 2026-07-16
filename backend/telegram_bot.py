import requests
import sqlite3
import time
import os
import json
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE  = os.path.join(BASE_DIR, 'redaman.db')
CFG_FILE = os.path.join(BASE_DIR, 'config.json')

TOKEN = ""
DASHBOARD_URL = "http://127.0.0.1:8000"
if os.path.exists(CFG_FILE):
    try:
        with open(CFG_FILE, "r") as _f:
            _cfg = json.load(_f)
            TOKEN = _cfg.get("telegram_token", "")
            DASHBOARD_URL = _cfg.get("dashboard_url", "http://127.0.0.1:8000")
    except:
        pass

bot = telebot.TeleBot(TOKEN)

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.row_factory = sqlite3.Row
    return conn

def get_reminder_minutes():
    try:
        with open(CFG_FILE) as f:
            return json.load(f).get('reminder_minutes', 60)
    except:
        return 60

def send_message(chat_id, text, reply_markup=None):
    try:
        markup = None
        if reply_markup and "inline_keyboard" in reply_markup:
            markup = InlineKeyboardMarkup()
            for row in reply_markup["inline_keyboard"]:
                btn_row = []
                for btn in row:
                    url = btn.get("url")
                    cb_data = btn.get("callback_data")
                    btn_row.append(InlineKeyboardButton(text=btn["text"], url=url, callback_data=cb_data))
                markup.row(*btn_row)
        bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup)
    except Exception as e:
        logging.error(f"Error send_message: {e}")

def send_message_with_buttons(chat_id, text, buttons):
    reply_markup = {"inline_keyboard": buttons}
    send_message(chat_id, text, reply_markup=reply_markup)

def edit_message(chat_id, message_id, text, reply_markup=None):
    try:
        markup = None
        if reply_markup and "inline_keyboard" in reply_markup:
            markup = InlineKeyboardMarkup()
            for row in reply_markup["inline_keyboard"]:
                btn_row = []
                for btn in row:
                    url = btn.get("url")
                    cb_data = btn.get("callback_data")
                    btn_row.append(InlineKeyboardButton(text=btn["text"], url=url, callback_data=cb_data))
                markup.row(*btn_row)
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup)
    except Exception as e:
        logging.error(f"Error edit_message: {e}")

def answer_callback(callback_query_id, text=""):
    try:
        bot.answer_callback_query(callback_query_id, text)
    except:
        pass

def rx_bar(rx):
    """Mengembalikan bar visual & label status berdasarkan dBm"""
    if rx is None:
        return "⚫ OFFLINE"
    if rx > -23.0:
        return f"🟢 {rx:.2f} dBm"
    elif rx >= -26.0:
        return f"🟡 {rx:.2f} dBm"
    else:
        return f"🔴 {rx:.2f} dBm"

def format_critical_table(rows, title="", page=1, page_size=10):
    """Format baris kritis sebagai tabel pre-formatted yang rapi"""
    lines = []
    if title:
        lines.append(title)
        lines.append("")

    total = len(rows)
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total)
    
    for i in range(start_idx, end_idx):
        row = rows[i]
        name = (row['customer_name'] or "Tanpa Nama")[:20]
        olt  = (row['olt_name'] or "?")[:12]
        rx   = row['rx_power']
        status_label = row['status'] if 'status' in row.keys() else 'CRITICAL'
        bar  = rx_bar(rx)

        if status_label == 'CRITICAL':
            badge = "🔴 CRT"
        elif status_label == 'WARNING':
            badge = "🟡 WRN"
        else:  # OFFLINE
            badge = "⚫ OFF"

        lines.append(f"<b>{i+1}. {name}</b> ({badge})")
        lines.append(f"   🖥 OLT  : {olt}")
        if status_label == 'OFFLINE':
            reason = (row['last_offline_reason'] or 'Unknown') if 'last_offline_reason' in row.keys() else 'Unknown'
            lines.append(f"   🔍 Alasan: {reason}")
        else:
            lines.append(f"   📶 Daya : {bar}")
        lines.append("")

    return "\n".join(lines).strip()

def send_or_edit_kritis(chat_id, message_id=None, page=1):
    PAGE_SIZE = 10
    conn = get_db_connection()
    try:
        criticals = conn.execute('''
            SELECT al.onu_id, al.customer_name, o.name as olt_name, al.status, al.last_offline_reason,
                   (SELECT rx_power FROM attenuations at
                    WHERE at.onu_id = al.onu_id AND at.olt_id = al.olt_id
                    ORDER BY at.timestamp DESC LIMIT 1) as rx_power
            FROM alert_states al
            JOIN olts o ON al.olt_id = o.id
            WHERE al.status IN ('WARNING', 'CRITICAL', 'OFFLINE')
            ORDER BY
                CASE al.status WHEN 'OFFLINE' THEN 0 WHEN 'CRITICAL' THEN 1 ELSE 2 END,
                rx_power ASC
        ''').fetchall()
    finally:
        conn.close()

    if not criticals:
        msg = "✅ <b>Semua pelanggan dalam kondisi AMAN!</b>\n\n<i>Tidak ada ONU dengan redaman buruk saat ini.</i>"
        buttons = [[{"text": "🔄 Refresh", "callback_data": "cmd_kritis"}]]
        if message_id:
            edit_message(chat_id, message_id, msg, {"inline_keyboard": buttons})
        else:
            send_message_with_buttons(chat_id, msg, buttons)
        return

    total = len(criticals)
    import math
    total_pages = math.ceil(total / PAGE_SIZE)
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    title = f"🔴 <b>DAFTAR PELANGGAN DOWN/WARNING</b>\n"
    title += f"Halaman <b>{page}/{total_pages}</b> (Total: {total} ONU)\n"
    title += f"{'─'*30}"
    
    msg = format_critical_table(criticals, title, page=page, page_size=PAGE_SIZE)
    msg += f"\n\n<i>Total: {total} pelanggan perlu perhatian!</i>"

    # Pagination buttons
    nav_row = []
    if page > 1:
        nav_row.append({"text": "⬅️ Sebelumnya", "callback_data": f"kritis_page_{page-1}"})
    if page < total_pages:
        nav_row.append({"text": "Berikutnya ➡️", "callback_data": f"kritis_page_{page+1}"})

    buttons = []
    if nav_row:
        buttons.append(nav_row)
        
    buttons.append([
        {"text": f"🔄 Refresh (Hal {page})", "callback_data": f"kritis_page_{page}"},
        {"text": "📊 Status", "callback_data": "cmd_status"}
    ])
    
    # Tambahkan link ke web dashboard (pre-filtered ke warning/critical)
    buttons.append([
        {"text": "🔴 Kritis (Web)", "url": f"{DASHBOARD_URL}/?filter=critical"},
        {"text": "🟡 Warning (Web)", "url": f"{DASHBOARD_URL}/?filter=warning"}
    ])

    reply_markup = {"inline_keyboard": buttons}
    if message_id:
        edit_message(chat_id, message_id, msg, reply_markup)
    else:
        send_message(chat_id, msg, reply_markup)


def do_live_check(chat_id, onu_id, olt_id, cust_name):
    conn = get_db_connection()
    try:
        olt = conn.execute("SELECT * FROM olts WHERE id = ?", (olt_id,)).fetchone()
    finally:
        conn.close()
    if not olt:
        send_message(chat_id, "❌ OLT tidak ditemukan.")
        return
    
    ip_port = olt['ip_port']
    community = olt['community']
    olt_name = olt['name']
    olt_type = olt['brand']

    send_message(chat_id, f"⏳ Menarik data LIVE untuk <b>{cust_name}</b> dari <b>{olt_name}</b>...")

    ip   = ip_port.rsplit(':', 1)[0]
    port = int(ip_port.rsplit(':', 1)[1])


    try:
        from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

        OIDS = {
            "HSGQ": {"name": "1.3.6.1.4.1.50224.3.12.2.1.2", "rx": "1.3.6.1.4.1.50224.3.12.3.1.4",
                     "offline": "1.3.6.1.4.1.50224.3.12.2.1.22", "version": 0},
            "VSOL": {"name": "1.3.6.1.4.1.37950.1.1.6.1.1.1.1.7", "rx": "1.3.6.1.4.1.37950.1.1.6.1.1.3.1.7",
                     "offline": "1.3.6.1.4.1.37950.1.1.6.1.1.1.1.10", "version": 1},
        }

        if olt_type not in OIDS:
            send_message(chat_id, f"❌ Tipe OLT <b>{olt_type}</b> belum didukung untuk LIVE CEK.")
            return

        cfg     = OIDS[olt_type]
        version = cfg["version"]
        oid_rx  = f'{cfg["rx"]}.{onu_id}' if olt_type == "VSOL" else f'{cfg["rx"]}.{onu_id}.0.0'
        oid_nm  = f'{cfg["name"]}.{onu_id}'

        it_rx = getCmd(SnmpEngine(), CommunityData(community, mpModel=version),
                       UdpTransportTarget((ip, port), timeout=5.0, retries=1),
                       ContextData(), ObjectType(ObjectIdentity(oid_rx)))
        errRx, _, _, vbRx = next(it_rx)

        it_nm = getCmd(SnmpEngine(), CommunityData(community, mpModel=version),
                       UdpTransportTarget((ip, port), timeout=5.0, retries=1),
                       ContextData(), ObjectType(ObjectIdentity(oid_nm)))
        errNm, _, _, vbNm = next(it_nm)

        if errRx or errNm:
            send_message(chat_id, f"❌ <b>GAGAL (Timeout)</b>\nOLT tidak merespon SNMP.\n<code>{errRx or errNm}</code>")
        else:
            val_rx = vbRx[0][1].prettyPrint()
            val_nm = vbNm[0][1].prettyPrint() or cust_name

            if "No Such" in val_rx or val_rx in ('0', 'None', ''):
                reason = "Unknown"
                oid_off = f'{cfg["offline"]}.{onu_id}'
                it_off = getCmd(SnmpEngine(), CommunityData(community, mpModel=version),
                                UdpTransportTarget((ip, port), timeout=3.0, retries=1),
                                ContextData(), ObjectType(ObjectIdentity(oid_off)))
                errOff, _, _, vbOff = next(it_off)
                if not errOff:
                    reason = vbOff[0][1].prettyPrint().strip() or "Unknown"
                send_message(chat_id,
                    f"⚠️ ONU <code>{onu_id}</code> (<b>{val_nm}</b>) sedang <b>OFFLINE</b>.\n"
                    f"🔍 Alasan / Last Trouble: <b>{reason}</b>")
            else:
                try:
                    if '.' in val_rx:
                        dbm = float(val_rx)
                    else:
                        val_int = int(val_rx)
                        dbm = val_int / 100.0 if olt_type == 'HSGQ' else val_int / 10.0
                except (ValueError, TypeError):
                    dbm = None

                bar = rx_bar(dbm)
                msg = (
                    f"⚡ <b>CEK LIVE ONU</b>\n"
                    f"{'─'*28}\n"
                    f"👤 Nama    : <b>{val_nm}</b>\n"
                    f"🆔 ONU ID  : <code>{onu_id}</code>\n"
                    f"🖥 OLT     : <b>{olt_name}</b>\n"
                    f"📶 Redaman : {bar}\n"
                    f"{'─'*28}\n"
                    f"🕐 Update  : <i>Real-time (detik ini)</i>"
                )
                send_message(chat_id, msg)

    except Exception as e:
        send_message(chat_id, f"❌ Error SNMP: <code>{e}</code>")

def handle_command(chat_id, text, message_id=None):
    parts = text.split()
    command = parts[0].lower().split("@")[0]   # strip @botname jika ada

    # ── /start ────────────────────────────────────────────────────
    if command == "/start":
        msg = (
            "👋 <b>Selamat datang di Bot NOC Redaman!</b>\n\n"
            "Pilih menu di bawah atau ketik perintah langsung:"
        )
        buttons = [
            [{"text": "📊 Status Sistem",       "callback_data": "cmd_status"},
             {"text": "🔴 Daftar Kritis",        "callback_data": "cmd_kritis"}],
            [{"text": "🔍 Cari Pelanggan",       "callback_data": "cmd_help_cari"},
             {"text": "⚡ Cek Live ONU",         "callback_data": "cmd_help_cek"}],
            [{"text": "⏱ Atur Interval Reminder","callback_data": "cmd_help_reminder"}],
            [{"text": "🖥 Buka Dashboard",       "url": f"{DASHBOARD_URL}/"}],
        ]
        send_message_with_buttons(chat_id, msg, buttons)

    # ── /status ───────────────────────────────────────────────────
    elif command == "/status":
        conn = get_db_connection()
        try:
            total_olt      = conn.execute("SELECT COUNT(*) FROM olts").fetchone()[0]
            critical_count = conn.execute("SELECT COUNT(*) FROM alert_states WHERE status='CRITICAL'").fetchone()[0]
            warning_count  = conn.execute("SELECT COUNT(*) FROM alert_states WHERE status='WARNING'").fetchone()[0]
            normal_count   = conn.execute("SELECT COUNT(*) FROM alert_states WHERE status='NORMAL'").fetchone()[0]
            total_onu      = conn.execute("SELECT COUNT(*) FROM alert_states").fetchone()[0]

            reminder_min = get_reminder_minutes()
        finally:
            conn.close()

        status_icon = "🔴" if critical_count > 0 else ("🟡" if warning_count > 0 else "✅")
        msg = (
            f"📊 <b>STATUS SISTEM NOC</b>\n"
            f"{'─'*28}\n"
            f"🖥  Total OLT Terdaftar : <b>{total_olt}</b>\n"
            f"📡  Total ONU Terpantau : <b>{total_onu}</b>\n"
            f"{'─'*28}\n"
            f"🟢  ONU Normal          : <b>{normal_count}</b>\n"
            f"🟡  ONU Warning (Light) : <b>{warning_count}</b>\n"
            f"🔴  ONU Kritis (Severe) : <b>{critical_count}</b>\n"
            f"{'─'*28}\n"
            f"⏱  Interval Reminder   : <b>{reminder_min} menit</b>\n"
        )
        buttons = [
            [{"text": "🔴 Kritis (Web)", "url": f"{DASHBOARD_URL}/?filter=critical"},
             {"text": "🟡 Warning (Web)", "url": f"{DASHBOARD_URL}/?filter=warning"}],
            [{"text": "🔄 Refresh Status", "callback_data": "cmd_status"},
             {"text": "🖥 Dashboard Utama", "url": f"{DASHBOARD_URL}/"}],
        ]
        send_message_with_buttons(chat_id, msg, buttons)

    # ── /kritis ───────────────────────────────────────────────────
    elif command == "/kritis":
        send_or_edit_kritis(chat_id, page=1)

    # ── /olt ──────────────────────────────────────────────────────
    elif command == "/olt":
        if len(parts) < 2:
            msg = (
                "⚠️ <b>Perintah /olt Tidak Lengkap</b>\n\n"
                "Gunakan format: <code>/olt [nama_olt]</code>\n"
                "Contoh: <code>/olt vsol</code> atau <code>/olt hsgq</code> \n\n"
                "<i>Menampilkan semua pelanggan di OLT tersebut beserta redamannya.</i>"
            )
            send_message(chat_id, msg)
            return
            
        search_term = " ".join(parts[1:]).lower()
        conn = get_db_connection()
        try:
            # Cari OLT berdasarkan nama (case-insensitive)
            olts = conn.execute("SELECT id, name FROM olts WHERE lower(name) LIKE ?", ('%' + search_term + '%',)).fetchall()
            if not olts:
                send_message(chat_id, f"❌ OLT yang mengandung kata '<b>{search_term}</b>' tidak ditemukan di database.")
                return
                
            olt_id = olts[0]['id']
            olt_name = olts[0]['name']
            
            # Ambil semua data pelanggan dari OLT tersebut beserta redaman valid terakhir
            results = conn.execute('''
                SELECT c.customer_name, c.onu_id, a.status,
                       (SELECT att.rx_power FROM attenuations att
                        WHERE att.onu_id = c.onu_id AND att.olt_id = c.olt_id AND att.rx_power IS NOT NULL
                        ORDER BY att.timestamp DESC LIMIT 1) as rx_power
                FROM onu_name_cache c
                LEFT JOIN alert_states a ON c.onu_id = a.onu_id AND c.olt_id = a.olt_id
                WHERE c.olt_id = ?
                ORDER BY 
                    CASE WHEN a.status = 'OFFLINE' THEN 4
                         WHEN a.status = 'CRITICAL' THEN 1 
                         WHEN a.status = 'WARNING' THEN 2 
                         ELSE 3 END,
                    rx_power ASC
            ''', (olt_id,)).fetchall()
            
            if results:
                total = len(results)
                msg = f"🖥 <b>Daftar Pelanggan OLT: {olt_name}</b>\n"
                msg += f"<i>Total: {total} ONU</i>\n{'─'*30}\n\n"
                
                # Telegram punya limit teks, kita batasi 50 row
                display_limit = min(total, 50)
                
                for row in results[:display_limit]:
                    name = (row['customer_name'] or "?")[:20]
                    rx = row['rx_power']
                    status = row['status'] or "NORMAL"
                    
                    if status == "OFFLINE":
                        msg += f"🔌 {name} | OFFLINE\n"
                    elif status == "CRITICAL":
                        msg += f"🔴 {name} | {rx} dBm\n"
                    elif status == "WARNING":
                        msg += f"🟡 {name} | {rx} dBm\n"
                    else:
                        msg += f"✅ {name} | {rx} dBm\n"
                        
                if total > display_limit:
                    msg += f"\n<i>...dan {total - display_limit} lainnya. Buka dashboard untuk full detail.</i>"
                    
                buttons = [
                    [{"text": f"🖥 Buka Dashboard ({olt_name})", "url": f"{DASHBOARD_URL}/?olt={olt_id}"}]
                ]
                send_message_with_buttons(chat_id, msg, buttons)
            else:
                send_message(chat_id, f"ℹ️ Belum ada data pelanggan untuk OLT <b>{olt_name}</b>.")
        finally:
            conn.close()

    # ── /cari ─────────────────────────────────────────────────────
    elif command == "/cari":
        if len(parts) < 2:
            msg = (
                "⚠️ <b>Format Pencarian Salah!</b>\n\n"
                "Cara Penggunaan:\n"
                "👉 <code>/cari budi</code>\n"
                "👉 <code>/cari siti rahma</code>\n\n"
                "<i>Fungsi: Mencari riwayat data pelanggan di Database.</i>"
            )
            send_message(chat_id, msg)
            return

        search_term = " ".join(parts[1:])
        conn = get_db_connection()
        try:
            results = conn.execute('''
                SELECT a.onu_id, a.customer_name, a.status, o.name as olt_name
                FROM alert_states a
                JOIN olts o ON a.olt_id = o.id
                WHERE a.customer_name LIKE ?
                LIMIT 5
            ''', ('%' + search_term + '%',)).fetchall()

            if results:
                msg = f"🔍 <b>HASIL PENCARIAN: '{search_term}'</b>\n{'─'*30}\n\n"
                for row in results:
                    atten = conn.execute('''
                        SELECT rx_power, timestamp
                        FROM attenuations
                        WHERE onu_id = ?
                        ORDER BY timestamp DESC LIMIT 1
                    ''', (row['onu_id'],)).fetchone()

                    rx   = atten['rx_power'] if atten else None
                    ts   = atten['timestamp'][:16] if atten and atten['timestamp'] else "N/A"
                    bar  = rx_bar(rx)
                    icon = "🔴" if row['status'] == 'CRITICAL' else "✅"

                    msg += (
                        f"{icon} <b>{row['customer_name']}</b>\n"
                        f"   🖥 OLT    : {row['olt_name']}\n"
                        f"   🆔 ONU ID : <code>{row['onu_id']}</code>\n"
                        f"   📶 Daya   : {bar}\n"
                        f"   🕐 Update : {ts}\n\n"
                    )
                send_message(chat_id, msg.strip())
            else:
                send_message(chat_id, f"❌ Pelanggan dengan nama '<b>{search_term}</b>' tidak ditemukan.")
        finally:
            conn.close()

    # ── /cek ─────────────────────────────────────────────────────
    elif command == "/cek":
        if len(parts) < 2:
            msg = (
                "⚠️ <b>Format Cek LIVE Salah!</b>\n\n"
                "Cara Penggunaan:\n"
                "👉 <code>/cek budi</code> (Cari by Nama)\n"
                "👉 <code>/cek 16777472</code> (Cari by ID)\n\n"
                "<i>Fungsi: Menarik data detik ini LANGSUNG dari OLT.</i>"
            )
            send_message(chat_id, msg)
            return

        def process_cek():
            query = " ".join(parts[1:])
            conn = get_db_connection()
            try:
                data_rows = conn.execute('''
                    SELECT c.onu_id, c.customer_name, o.ip_port, o.community,
                           o.name as olt_name, o.brand as olt_type, o.id as olt_id
                    FROM onu_name_cache c
                    JOIN olts o ON c.olt_id = o.id
                    WHERE c.onu_id = ? OR c.customer_name LIKE ?
                    ORDER BY 
                        CASE WHEN c.customer_name COLLATE NOCASE = ? THEN 1
                             WHEN c.customer_name LIKE ? THEN 2
                             ELSE 3 END,
                        LENGTH(c.customer_name) ASC
                    LIMIT 5
                ''', (query, '%' + query + '%', query, query + '%')).fetchall()
                
                matches = [dict(r) for r in data_rows]

                # Jika tidak ditemukan di cache → walk LIVE ke semua OLT
                if not matches:
                    all_olts = conn.execute('SELECT id, name, ip_port, community, brand FROM olts').fetchall()
                    
                    send_message(chat_id,
                        f"🔍 '<b>{query}</b>' tidak ada di cache.\n"
                        f"⏳ Sedang walk LIVE ke <b>{len(all_olts)} OLT</b>... harap tunggu sebentar."
                    )

                    from pysnmp.hlapi import nextCmd, getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

                    OID_CFG = {
                        "HSGQ": {"name": "1.3.6.1.4.1.50224.3.12.2.1.2", "version": 0},
                        "VSOL": {"name": "1.3.6.1.4.1.37950.1.1.6.1.1.1.1.7", "version": 1},
                    }

                    for olt_row in all_olts:
                        olt_id_val    = olt_row['id']
                        olt_name_val  = olt_row['name']
                        olt_ip_port   = olt_row['ip_port']
                        olt_comm      = olt_row['community']
                        olt_brand     = olt_row['brand']

                        if olt_brand not in OID_CFG:
                            continue

                        cfg     = OID_CFG[olt_brand]
                        ip      = olt_ip_port.rsplit(':', 1)[0]
                        port    = int(olt_ip_port.rsplit(':', 1)[1])
                        version = cfg['version']

                        exact_found = False
                        try:
                            for (errInd, errStat, _, vBinds) in nextCmd(
                                SnmpEngine(),
                                CommunityData(olt_comm, mpModel=version),
                                UdpTransportTarget((ip, port), timeout=5.0, retries=1),
                                ContextData(),
                                ObjectType(ObjectIdentity(cfg['name'])),
                                lexicographicMode=False
                            ):
                                if errInd or errStat:
                                    break
                                for vb in vBinds:
                                    oid_str   = vb[0].prettyPrint()
                                    val_str   = vb[1].prettyPrint().strip()
                                    parts_oid = oid_str.split('.')

                                    if olt_brand == 'VSOL':
                                        onu_idx = f"{parts_oid[-2]}.{parts_oid[-1]}"
                                    else:
                                        onu_idx = parts_oid[-1]

                                    if query.lower() == val_str.lower() or onu_idx == query:
                                        matches = [{
                                            'onu_id':        onu_idx,
                                            'customer_name': val_str,
                                            'ip_port':       olt_ip_port,
                                            'community':     olt_comm,
                                            'olt_name':      olt_name_val,
                                            'olt_type':      olt_brand,
                                            'olt_id':        olt_id_val,
                                        }]
                                        exact_found = True
                                        break
                                    elif query.lower() in val_str.lower():
                                        if len(matches) < 5:
                                            matches.append({
                                                'onu_id':        onu_idx,
                                                'customer_name': val_str,
                                                'ip_port':       olt_ip_port,
                                                'community':     olt_comm,
                                                'olt_name':      olt_name_val,
                                                'olt_type':      olt_brand,
                                                'olt_id':        olt_id_val,
                                            })
                                if exact_found:
                                    break
                        except Exception as e:
                            print(f"[/cek walk error] OLT {olt_name_val}: {e}")

                        if exact_found:
                            break

                    # Simpan matches ke cache
                    if matches:
                        conn2 = get_db_connection()
                        try:
                            for m in matches:
                                conn2.execute(
                                    'INSERT OR REPLACE INTO onu_name_cache '
                                    '(onu_id, olt_id, customer_name, last_updated) VALUES (?,?,?,datetime("now","localtime"))',
                                    (m['onu_id'], m['olt_id'], m['customer_name'])
                                )
                            conn2.commit()
                        finally:
                            conn2.close()

            finally:
                conn.close()

            if not matches:
                send_message(chat_id,
                    f"❌ ONU '<b>{query}</b>' tidak ditemukan di database maupun di OLT.\n"
                    f"<i>Pastikan nama sudah diinput dan ONU sudah terhubung secara fisik ke OLT.</i>"
                )
                return

            if len(matches) == 1:
                m = matches[0]
                do_live_check(chat_id, m['onu_id'], m['olt_id'], m['customer_name'])
            else:
                buttons = []
                for m in matches:
                    name_btn = m['customer_name'][:30]
                    cb_data = f"cek_live_{m['onu_id']}_{m['olt_id']}"
                    buttons.append([{"text": name_btn, "callback_data": cb_data}])
                
                msg = f"🔍 Ditemukan {len(matches)} pelanggan dengan nama mirip.\nSilakan klik salah satu:"
                send_message_with_buttons(chat_id, msg, buttons)

        import threading
        threading.Thread(target=process_cek).start()

    # ── /set_reminder ─────────────────────────────────────────────
    elif command == "/set_reminder":
        if len(parts) < 2:
            msg = (
                "⚠️ <b>Format Set Reminder Salah!</b>\n\n"
                "Cara Penggunaan:\n"
                "👉 <code>/set_reminder 3</code>  → tiap 3 menit\n"
                "👉 <code>/set_reminder 10</code> → tiap 10 menit\n"
                "👉 <code>/set_reminder 60</code> → tiap 1 jam\n\n"
                "<i>Fungsi: Mengatur jarak waktu pengiriman BULK reminder untuk pelanggan yang masih kritis.</i>"
            )
            send_message(chat_id, msg)
            return

        try:
            menit = int(parts[1])
            if menit < 1:
                send_message(chat_id, "⚠️ Menit harus lebih dari 0.")
                return

            cfg = {"reminder_minutes": 60}
            if os.path.exists(CFG_FILE):
                with open(CFG_FILE, "r") as f:
                    cfg = json.load(f)

            cfg["reminder_minutes"] = menit
            with open(CFG_FILE, "w") as f:
                json.dump(cfg, f)

            msg = (
                f"✅ <b>Interval Reminder Diperbarui!</b>\n"
                f"{'─'*28}\n"
                f"⏱ Interval baru : <b>{menit} menit</b>\n"
                f"{'─'*28}\n"
                f"<i>Reminder BULK berikutnya akan dikirim {menit} menit setelah reminder terakhir.</i>"
            )
            send_message(chat_id, msg)

        except ValueError:
            send_message(chat_id, "⚠️ Masukkan angka menit yang valid.\nContoh: <code>/set_reminder 10</code>")

def handle_callback(callback_query):
    """Handle tombol inline keyboard"""
    cid  = callback_query["id"]
    chat = callback_query["message"]["chat"]["id"]
    data = callback_query.get("data", "")

    answer_callback(cid)

    if data == "cmd_status":
        handle_command(chat, "/status")
    elif data == "cmd_kritis":
        send_or_edit_kritis(chat, page=1)
    elif data.startswith("kritis_page_"):
        try:
            p = int(data.split("_")[-1])
            mid = callback_query["message"]["message_id"]
            send_or_edit_kritis(chat, message_id=mid, page=p)
        except Exception as e:
            print("Error in callback pagination:", e)
    elif data == "cmd_help_cari":
        handle_command(chat, "/cari")
    elif data == "cmd_help_cek":
        handle_command(chat, "/cek")
    elif data == "cmd_help_reminder":
        handle_command(chat, "/set_reminder")
    elif data.startswith("cek_"):
        parts = data.split("_")
        if len(parts) >= 3:
            onu_id = parts[-2]
            olt_id = parts[-1]
            conn = get_db_connection()
            try:
                row = conn.execute("SELECT customer_name FROM onu_name_cache WHERE onu_id=? AND olt_id=?", (onu_id, olt_id)).fetchone()
            finally:
                conn.close()
            cust_name = row['customer_name'] if row else f"ONU-{onu_id}"
            
            # Use threading so bot doesn't block
            import threading
            threading.Thread(target=do_live_check, args=(chat, onu_id, olt_id, cust_name)).start()

@bot.message_handler(commands=['start', 'status', 'kritis', 'cari', 'cek', 'set_reminder'])
def bot_handle_command(message):
    handle_command(message.chat.id, message.text, message.message_id)

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/'))
def bot_handle_any_command(message):
    handle_command(message.chat.id, message.text, message.message_id)

@bot.callback_query_handler(func=lambda call: True)
def bot_handle_callback(call):
    callback_query = {
        "id": call.id,
        "message": {"chat": {"id": call.message.chat.id}, "message_id": call.message.message_id},
        "data": call.data
    }
    handle_callback(callback_query)

def main():
    print("Bot NOC Redaman - Listener aktif (Powered by Telebot)...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            logging.error(f"Telebot polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
