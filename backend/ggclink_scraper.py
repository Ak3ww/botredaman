import requests
import hashlib
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import traceback

def get_session_with_retries():
    session = requests.Session()
    # Auto retry up to 3 times for transient connection errors
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def pull_ggclink_data(ip, port, username, password):
    url = f'http://{ip}:{port}'
    headers = {
        'Referer': f'{url}/login.html',
        'User-Agent': 'Mozilla/5.0'
    }

    # GGCLINK uses a hardcoded salt 'an3400'
    m = hashlib.md5()
    m.update(('an3400' + password).encode('utf-8'))
    pwd_md5 = m.hexdigest()

    session = get_session_with_retries()
    login_success = False

    try:
        # 1. Login
        r = session.post(f'{url}/setModules', headers=headers, json={'login': {'username': username, 'password': pwd_md5}}, timeout=15)
        if r.status_code != 200 or r.json().get('errorCode') != 0:
            print(f"  [GGCLINK] Gagal login ke {ip}:{port} - {r.status_code} - {r.text}")
            return None, None, None, None, None, None, None
            
        login_success = True
        headers['token'] = r.headers.get('token', '')

        # 2. Fetch PON topology
        r_slot = session.post(f'{url}/getModules', headers=headers, json={'slotInfo': ''}, timeout=15)
        slot_data = r_slot.json()
        if slot_data.get('errCode') == "-1" or (slot_data.get('errorCode') is not None and slot_data.get('errorCode') != 0):
            print(f"  [GGCLINK] Warning: Invalid slotInfo response: {slot_data}")
            return None, None, None, None, None, None, None
            
        # 2.5 Fetch current alarms for offline reason binding
        alarm_map = {}
        try:
            r_alarm = session.post(f'{url}/getModules', headers=headers, json={'currentAlarm': {'pageNum': 1, 'pageCount': 500}}, timeout=15)
            alarm_json = r_alarm.json()
            if alarm_json.get('errCode') != "-1" and (alarm_json.get('errorCode') is None or alarm_json.get('errorCode') == 0):
                for a in alarm_json.get('currentAlarm', {}).get('list', []):
                    src = str(a.get('source', '')).strip().lower()
                    a_type = str(a.get('type', ''))
                    reason = a_type.split('=', 1)[1].strip() if '=' in a_type else a_type.strip()
                    if src not in alarm_map:
                        alarm_map[src] = reason
        except Exception as e:
            print(f"  [GGCLINK] Warning: Failed to fetch currentAlarm: {e}")
        
        rx_data = {}
        status_data = {}
        uptime_data = {}
        downtime_data = {}
        offline_data = {}
        alive_data = {}
        all_onus = {}
        
        for slot in slot_data.get('slotInfo', []):
            slot_id = slot.get('slotId')
            pons = slot.get('pons', [])
            
            # Fetch ALL core data in one request (works on both firmware versions)
            core_payload = {
                'onuLightInfo': {'slotNumber': slot_id, 'ponPort': 0, 'pageNum': 1, 'pageCount': 500},
                'authorizedList': {'slotNumber': slot_id, 'ponPort': 0, 'pageNum': 1, 'pageCount': 500}
            }
            r_core = session.post(f'{url}/getModules', headers=headers, json=core_payload, timeout=20)
            core_json = r_core.json()
            
            # Fetch extra status data (works on GGCLINK-02, fails gracefully on GGCLINK-01)
            stat_payload = {
                'ontStatusInfo': {'slotNumber': slot_id, 'ponPort': 0, 'pageNum': 1, 'pageCount': 500}
            }
            r_stat = session.post(f'{url}/getModules', headers=headers, json=stat_payload, timeout=20)
            stat_json = r_stat.json()
            
            stat_list = []
            if stat_json.get('errCode') != "-1" and (stat_json.get('errorCode') is None or stat_json.get('errorCode') == 0):
                stat_list = stat_json.get('ontStatusInfo', {}).get('list', [])
                
            light_list = []
            if core_json.get('errCode') != "-1" and (core_json.get('errorCode') is None or core_json.get('errorCode') == 0):
                light_list = core_json.get('onuLightInfo', {}).get('list', [])
                
            auth_list = []
            if core_json.get('errCode') != "-1" and (core_json.get('errorCode') is None or core_json.get('errorCode') == 0):
                auth_list = core_json.get('authorizedList', {}).get('list', [])
                
            stat_map = {item['ont']: item for item in stat_list if 'ont' in item}
            light_map = {item['ont']: item for item in light_list if 'ont' in item}
            auth_map = {item['ont']: item for item in auth_list if 'ont' in item}
            
            for pon in pons:
                pon_id = pon.get('ponId')
                onus_meta = pon.get('onus', [])
                for onu in onus_meta:
                    authid = onu.get('authid')
                    onu_idx = (slot_id * 100000) + (pon_id * 1000) + authid
                    
                    ont_str = onu.get('name')
                    sn = onu.get('sn')
                    
                    st = stat_map.get(ont_str, {})
                    lt = light_map.get(ont_str, {})
                    at = auth_map.get(ont_str, {})
                    
                    customer = at.get('ontName') or st.get('ontName') or lt.get('ontName') or onu.get('ontName') or st.get('authDesc') or f"ONU-{ont_str}"
                    if not customer.strip():
                        customer = f"ONU-{ont_str}"
                    
                    model = at.get('model') or st.get('equipmentId') or onu.get('onuModel') or ''
                    all_onus[onu_idx] = {'customer': customer, 'sn': sn, 'version': model}
                    
                    if 'status' in at:
                        is_online = str(at['status']).lower() in ['online', '1']
                        status_data[onu_idx] = '1' if is_online else '0'
                    elif 'phaseState' in st:
                        is_online = str(st['phaseState']).lower() in ['working', '1']
                        status_data[onu_idx] = '1' if is_online else '0'
                    elif 'status' in st:
                        is_online = str(st['status']).lower() in ['online', '1']
                        status_data[onu_idx] = '1' if is_online else '0'
                    else:
                        status_data[onu_idx] = None
                    
                    dbm = lt.get('rxPower') or lt.get('receivePower') or onu.get('rxPower') or onu.get('receivePower')
                    if dbm is not None:
                        try:
                            rx_val = float(dbm)
                            if rx_val < -40 or rx_val > 0:
                                rx_data[onu_idx] = None
                            else:
                                rx_data[onu_idx] = rx_val * 100
                        except:
                            rx_data[onu_idx] = None
                    else:
                        rx_data[onu_idx] = None
                        
                    on_time = at.get('onlineTime') or st.get('aliveTime') or st.get('onlineTime')
                    if on_time is not None:
                        try:
                            t_val = int(str(on_time).strip())
                            alive_data[onu_idx] = t_val * 100
                            uptime_data[onu_idx] = t_val * 100
                        except:
                            pass
                            
                    off_time = st.get('offlineTime')
                    if off_time is not None:
                        try:
                            downtime_data[onu_idx] = int(str(off_time).strip()) * 100
                        except:
                            pass
                            
                    off_reason = st.get('deregisterReason') or st.get('offlineReason')
                    if not off_reason:
                        ont_str_1 = f"ont {pon_id}:{authid}"
                        ont_str_2 = f"ont {slot_id}:{pon_id}:{authid}"
                        off_reason = alarm_map.get(ont_str_1) or alarm_map.get(ont_str_2)
                        
                    if off_reason:
                        offline_data[onu_idx] = str(off_reason)

        return rx_data, uptime_data, downtime_data, offline_data, alive_data, status_data, all_onus

    except Exception as e:
        print(f"  [Error] Parsing ONU GGCLINK: {e}")
        traceback.print_exc()
        return None, None, None, None, None, None, None
        
    finally:
        # ABSOLUTELY CRITICAL: ALWAYS LOGOUT to prevent zombie sessions clogging the OLT
        if login_success:
            try:
                session.post(f'{url}/setModules', headers=headers, json={'logout': {}}, timeout=5)
                session.close()
            except Exception as e:
                print(f"  [Warning] Failed to logout from GGCLINK {ip}: {e}")
