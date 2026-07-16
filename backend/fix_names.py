import sqlite3
import routeros_api

def get_mikrotik_secrets():
    try:
        connection = routeros_api.RouterOsApiPool('103.157.79.178', username='billinghub.id', password='@eugine0909@', port=8520, plaintext_login=True)
        api = connection.get_api()
        secrets = api.get_resource('/ppp/secret').get()
        connection.disconnect()
        return secrets
    except Exception as e:
        print(f"Error: {e}")
        return []

def fix_names():
    db = sqlite3.connect('C:\\BotRedaman\\backend\\redaman.db')
    cursor = db.cursor()
    
    secrets = get_mikrotik_secrets()
    if not secrets:
        print("Failed to get mikrotik secrets")
        return
        
    mikrotik_map = {}
    for s in secrets:
        name = s.get('name', '')
        comment = s.get('comment', '')
        if 'Pelanggan:' in comment:
            real_name = comment.split('Pelanggan:')[1].strip()
        else:
            real_name = name
            
        mikrotik_map[name.upper()] = real_name
        mikrotik_map[name.lower()] = real_name
        mikrotik_map[name] = real_name
        mikrotik_map[real_name.upper()] = real_name
        
    cursor.execute("SELECT sn, customer_name FROM onu_name_cache")
    onus = cursor.fetchall()
    
    count = 0
    for sn, cust_name in onus:
        if not cust_name:
            continue
            
        # Check if the current name is a PPP name (like EMG248 or FAS013)
        # OR if it matches any real_name
        if cust_name in mikrotik_map:
            real_name = mikrotik_map[cust_name]
            if cust_name != real_name:
                cursor.execute("UPDATE onu_name_cache SET customer_name = ? WHERE sn = ?", (real_name, sn))
                count += cursor.rowcount
                print(f"Fixed name: {cust_name} -> {real_name}")
                
    db.commit()
    db.close()
    print(f"Fixed {count} records to use actual names.")

if __name__ == '__main__':
    fix_names()
