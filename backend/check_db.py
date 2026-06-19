import sqlite3
c=sqlite3.connect('redaman.db').cursor()
print(c.execute('SELECT COUNT(id) FROM attenuations WHERE olt_id IN (3, 4)').fetchone()[0])
print(c.execute('SELECT COUNT(onu_id) FROM onu_name_cache WHERE olt_id IN (3, 4)').fetchone()[0])