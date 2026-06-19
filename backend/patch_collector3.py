import sys
import re

content = open('C:/BotRedaman/backend/collector.py', 'r', encoding='utf-8').read()

if 'from concurrent.futures import ThreadPoolExecutor' not in content:
    content = content.replace('import time', 'import time\nfrom concurrent.futures import ThreadPoolExecutor, as_completed')

old_mikrotik_fetch = '''    # Ambil data Mikrotik di awal siklus
    try:
        print("  [Mikrotik] Menarik data sesi PPPoE & traffic bandwidth...")
        active_users, queues_traffic, ppp_secrets = get_mikrotik_data()
        print(f"  [Mikrotik] Berhasil menarik {len(active_users)} user aktif dan {len(ppp_secrets)} secrets.")
    except Exception as e:
        print(f"  [WARN] Gagal menarik data Mikrotik: {e}")
        active_users, queues_traffic, ppp_secrets = [], {}, {}'''

new_mikrotik_fetch = '''    # Fetch Mikrotik in a separate function to be run in executor
    def fetch_mikrotik():
        try:
            return get_mikrotik_data()
        except Exception as e:
            print(f"  [WARN] Gagal menarik data Mikrotik: {e}")
            return [], {}, {}'''

content = content.replace(old_mikrotik_fetch, new_mikrotik_fetch)

old_olt_loop_start = '''    olts = cursor.execute('SELECT id, name, ip_port, brand, community FROM olts').fetchall()

    for olt_id, olt_name, ip_port, olt_brand, community in olts:
        if olt_brand != "GGCLINK" and olt_brand not in OIDS:
            print(f"  Skip {olt_name}: Brand '{olt_brand}' tidak dikenal.")
            continue

        cfg = OIDS.get(olt_brand, {})

        ip, port = ip_port.rsplit(':', 1)
        port = int(port)

        status_data = {}
        rx_data = {}
        up_time_data = {}
        down_time_data = {}
        offline_data = {}
        alive_data = {}
        
        if olt_brand == "GGCLINK":
            print(f"  [{olt_name}] Menarik data GGCLINK via HTTP API...")
            if "8002" in str(port):
                from ggclink_scraper import pull_ggclink_data
                rx_data, up_time_data, down_time_data, offline_data, alive_data, status_data, all_onus = pull_ggclink_data(ip, "8002", "root", "#eugine0909")
            else:
                from ggclink_scraper import pull_ggclink_data
                rx_data, up_time_data, down_time_data, offline_data, alive_data, status_data, all_onus = pull_ggclink_data(ip, "8001", "root", "#eugine0909")
            
            if rx_data is None:
                print(f"  [GGCLINK] Gagal menarik data dari {olt_name}. Cek koneksi atau login.")
                continue
            print(f"  [{olt_name}] Data diterima dari API GGCLINK.")
            current_snmp_ids = list(all_onus.keys())
        else:
            cached = cursor.execute('SELECT onu_id, customer_name FROM onu_name_cache WHERE olt_id = ?', (olt_id,)).fetchall()
            all_onus = {r[0]: r[1] for r in cached}

            print(f"  [{olt_name}] Menarik data SNMP...")
            try:
                # Fallback to standard SNMP scraper
                rx_raw = get_snmp_walk(ip, port, community, cfg["rx"], version=cfg["vsnmp"])
                if not rx_raw:
                    print(f"  [{olt_name}] Gagal / Timeout SNMP. Melewati OLT ini.")
                    continue
                for onu_idx, val in rx_raw.items():
                    rx_data[onu_idx] = val

                st_raw = get_snmp_walk(ip, port, community, cfg["status"], version=cfg["vsnmp"])
                if st_raw:
                    for onu_idx, val in st_raw.items():
                        status_data[onu_idx] = val
                        
                off_raw = get_snmp_walk(ip, port, community, cfg["offline"], version=cfg["vsnmp"])
                if off_raw:
                    for onu_idx, val in off_raw.items():
                        offline_data[onu_idx] = val

                up_raw = get_snmp_walk(ip, port, community, cfg["uptime"], version=cfg["vsnmp"])
                if up_raw:
                    for onu_idx, val in up_raw.items():
                        up_time_data[onu_idx] = val
                
                dn_raw = get_snmp_walk(ip, port, community, cfg["downtime"], version=cfg["vsnmp"])
                if dn_raw:
                    for onu_idx, val in dn_raw.items():
                        down_time_data[onu_idx] = val

                alv_raw = get_snmp_walk(ip, port, community, cfg["alive"], version=cfg["vsnmp"])
                if alv_raw:
                    for onu_idx, val in alv_raw.items():
                        alive_data[onu_idx] = val

                print(f"  [{olt_name}] Data diterima dari SNMP.")
                
            except Exception as e:
                print(f"  [{olt_name}] Error fatal saat SNMP walk: {e}")
                continue

            current_snmp_ids = list(rx_data.keys())'''

new_olt_loop_start = '''    olts = cursor.execute('SELECT id, name, ip_port, brand, community FROM olts').fetchall()
    
    # Ambil semua data all_onus terlebih dahulu untuk SNMP OLTs
    all_onus_db = {}
    for olt in olts:
        cached = cursor.execute('SELECT onu_id, customer_name FROM onu_name_cache WHERE olt_id = ?', (olt[0],)).fetchall()
        all_onus_db[olt[0]] = {r[0]: r[1] for r in cached}

    def fetch_olt(olt_id, olt_name, ip_port, olt_brand, community):
        if olt_brand != "GGCLINK" and olt_brand not in OIDS:
            return None
        cfg = OIDS.get(olt_brand, {})
        ip, port = ip_port.rsplit(':', 1)
        port = int(port)
        
        status_data, rx_data, up_time_data, down_time_data, offline_data, alive_data = {}, {}, {}, {}, {}, {}
        all_onus = all_onus_db.get(olt_id, {})
        current_snmp_ids = []

        if olt_brand == "GGCLINK":
            if "8002" in str(port):
                from ggclink_scraper import pull_ggclink_data
                rx_data, up_time_data, down_time_data, offline_data, alive_data, status_data, all_onus = pull_ggclink_data(ip, "8002", "root", "#eugine0909")
            else:
                from ggclink_scraper import pull_ggclink_data
                rx_data, up_time_data, down_time_data, offline_data, alive_data, status_data, all_onus = pull_ggclink_data(ip, "8001", "root", "#eugine0909")
            if rx_data is None:
                return None
            current_snmp_ids = list(all_onus.keys())
        else:
            rx_raw = get_snmp_walk(ip, port, community, cfg["rx"], version=cfg["vsnmp"])
            if not rx_raw:
                return None
            for onu_idx, val in rx_raw.items(): rx_data[onu_idx] = val
            st_raw = get_snmp_walk(ip, port, community, cfg["status"], version=cfg["vsnmp"])
            if st_raw:
                for onu_idx, val in st_raw.items(): status_data[onu_idx] = val
            off_raw = get_snmp_walk(ip, port, community, cfg["offline"], version=cfg["vsnmp"])
            if off_raw:
                for onu_idx, val in off_raw.items(): offline_data[onu_idx] = val
            up_raw = get_snmp_walk(ip, port, community, cfg["uptime"], version=cfg["vsnmp"])
            if up_raw:
                for onu_idx, val in up_raw.items(): up_time_data[onu_idx] = val
            dn_raw = get_snmp_walk(ip, port, community, cfg["downtime"], version=cfg["vsnmp"])
            if dn_raw:
                for onu_idx, val in dn_raw.items(): down_time_data[onu_idx] = val
            alv_raw = get_snmp_walk(ip, port, community, cfg["alive"], version=cfg["vsnmp"])
            if alv_raw:
                for onu_idx, val in alv_raw.items(): alive_data[onu_idx] = val
            current_snmp_ids = list(rx_data.keys())

        return (olt_id, olt_name, ip, port, olt_brand, community, cfg, rx_data, up_time_data, down_time_data, offline_data, alive_data, status_data, all_onus, current_snmp_ids)

    # ------------------ MULTI-THREADING FETCH ------------------
    print("  [INFO] Menarik data dari Mikrotik dan OLT secara paralel...")
    mikrotik_future = None
    olt_futures = {}
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        mikrotik_future = executor.submit(fetch_mikrotik)
        for olt in olts:
            olt_futures[executor.submit(fetch_olt, *olt)] = olt

    active_users, queues_traffic, ppp_secrets = mikrotik_future.result()
    print(f"  [Mikrotik] Berhasil menarik {len(active_users)} user aktif dan {len(ppp_secrets)} secrets.")

    secret_map = {}
    username_to_comment = {}
    for comment, secret_name in ppp_secrets.items():
        clean_comment = comment.upper().replace("PELANGGAN:", "").strip()
        normalized_key = clean_comment.replace(" ", "").replace("-", "")
        secret_map[normalized_key] = secret_name
        username_to_comment[secret_name] = comment.replace("Pelanggan:", "").replace("pelanggan:", "").strip()

    active_usernames = {u.get("name") for u in active_users if u.get("name")}

    # Proses hasil OLTs
    for future in as_completed(olt_futures):
        res = future.result()
        if res is None:
            continue
        olt_id, olt_name, ip, port, olt_brand, community, cfg, rx_data, up_time_data, down_time_data, offline_data, alive_data, status_data, all_onus, current_snmp_ids = res
        print(f"  [{olt_name}] Data berhasil ditarik dan siap diproses.")'''

content = content.replace(old_olt_loop_start, new_olt_loop_start)

# Add logging
import_logging = "import logging\n"
if "import logging" not in content:
    content = import_logging + content
    
content = content.replace('print(f"  [Error] ONU {onu_idx}: {e}")', 'logging.error(f"  [Error] ONU {onu_idx}: {e}", exc_info=True)')
content = content.replace('print(f"[FATAL] Error loop utama: {e}")', 'logging.error(f"[FATAL] Error loop utama: {e}", exc_info=True)')

# Configure logging at the bottom
if "logging.basicConfig" not in content:
    log_config = '''logging.basicConfig(filename='system.log', level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
'''
    content = content.replace('if __name__ == "__main__":', log_config + '\nif __name__ == "__main__":')

with open('C:/BotRedaman/backend/collector.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch collector complete!")
