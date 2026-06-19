import re

with open('telegram_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

do_live_check_code = """
def do_live_check(chat_id, onu_id, olt_id, cust_name):
    conn = get_db_connection()
    olt = conn.execute("SELECT * FROM olts WHERE id = ?", (olt_id,)).fetchone()
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
            send_message(chat_id, f"❌ <b>GAGAL (Timeout)</b>\\nOLT tidak merespon SNMP.\\n<code>{errRx or errNm}</code>")
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
                    f"⚠️ ONU <code>{onu_id}</code> (<b>{val_nm}</b>) sedang <b>OFFLINE</b>.\\n"
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
                    f"⚡ <b>CEK LIVE ONU</b>\\n"
                    f"{'─'*28}\\n"
                    f"👤 Nama    : <b>{val_nm}</b>\\n"
                    f"🆔 ONU ID  : <code>{onu_id}</code>\\n"
                    f"🖥 OLT     : <b>{olt_name}</b>\\n"
                    f"📶 Redaman : {bar}\\n"
                    f"{'─'*28}\\n"
                    f"🕐 Update  : <i>Real-time (detik ini)</i>"
                )
                send_message(chat_id, msg)

    except Exception as e:
        send_message(chat_id, f"❌ Error SNMP: <code>{e}</code>")

def handle_command"""

content = content.replace("def handle_command", do_live_check_code)

cek_pattern = re.compile(r'(    elif command == "/cek":.*?)(    # ── /set_reminder ─────────────────────────────────────────────)', re.DOTALL)

cek_new_logic = """    elif command == "/cek":
        if len(parts) < 2:
            msg = (
                "⚠️ <b>Format Cek LIVE Salah!</b>\\n\\n"
                "Cara Penggunaan:\\n"
                "👉 <code>/cek budi</code> (Cari by Nama)\\n"
                "👉 <code>/cek 16777472</code> (Cari by ID)\\n\\n"
                "<i>Fungsi: Menarik data detik ini LANGSUNG dari OLT.</i>"
            )
            send_message(chat_id, msg)
            return

        query = " ".join(parts[1:])
        conn = get_db_connection()
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
                f"🔍 '<b>{query}</b>' tidak ada di cache.\\n"
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
            conn2 = get_db_connection()
            for m in matches:
                conn2.execute(
                    'INSERT OR REPLACE INTO onu_name_cache '
                    '(onu_id, olt_id, customer_name, last_updated) VALUES (?,?,?,datetime("now","localtime"))',
                    (m['onu_id'], m['olt_id'], m['customer_name'])
                )
            conn2.commit()
            conn2.close()

        conn.close()

        if not matches:
            send_message(chat_id,
                f"❌ ONU '<b>{query}</b>' tidak ditemukan di database maupun di OLT.\\n"
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
            
            msg = f"🔍 Ditemukan {len(matches)} pelanggan dengan nama mirip.\\nSilakan klik salah satu:"
            send_message_with_buttons(chat_id, msg, buttons)

"""
content = cek_pattern.sub(cek_new_logic + r'\2', content)

callback_pattern = re.compile(r'(    elif data == "cmd_help_cek":\n        handle_command\(chat, "/cek"\)\n)(.*?def process_update)', re.DOTALL)
new_callback_logic = r"""\1    elif data.startswith("cek_live_"):
        parts = data.split("_")
        if len(parts) == 4:
            onu_id = parts[2]
            olt_id = parts[3]
            conn = get_db_connection()
            cached = conn.execute("SELECT customer_name FROM onu_name_cache WHERE onu_id=? AND olt_id=?", (onu_id, olt_id)).fetchone()
            conn.close()
            cust_name = cached['customer_name'] if cached else "Unknown"
            do_live_check(chat, onu_id, olt_id, cust_name)
\2"""
content = callback_pattern.sub(new_callback_logic, content)

with open('telegram_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)
