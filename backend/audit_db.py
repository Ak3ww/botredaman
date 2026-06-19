import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

c = sqlite3.connect('redaman.db')

tables = ['olts', 'attenuations', 'alert_states', 'onu_name_cache']
for t in tables:
    cols = c.execute(f'PRAGMA table_info({t})').fetchall()
    count = c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
    print(f'\n=== {t} ({count} rows) ===')
    for col in cols:
        print(f'  {col[1]:25} {col[2]:15} pk={col[5]} notNull={col[3]}')

# Check attenuations growth rate
print('\n=== ATTENUATIONS GROWTH ===')
rows = c.execute('''
    SELECT DATE(timestamp) as d, COUNT(*) as n 
    FROM attenuations 
    GROUP BY DATE(timestamp) 
    ORDER BY d DESC LIMIT 5
''').fetchall()
for r in rows: print(f'  {r}')

# Check alert_states sample
print('\n=== ALERT STATES SAMPLE ===')
rows = c.execute('''
    SELECT onu_id, customer_name, status, last_alert_time 
    FROM alert_states 
    WHERE status != 'NORMAL' 
    ORDER BY last_alert_time DESC LIMIT 5
''').fetchall()
for r in rows: print(f'  {r}')

# Check OLT structure
print('\n=== OLTS ===')
rows = c.execute('SELECT * FROM olts').fetchall()
for r in rows: print(f'  {r}')

# Check onu_name_cache sample with SN
print('\n=== ONU CACHE SAMPLE (WITH SN) ===')
rows = c.execute('SELECT customer_name, sn, firmware_version FROM onu_name_cache WHERE sn IS NOT NULL AND sn != "" LIMIT 5').fetchall()
for r in rows: print(f'  {r}')
