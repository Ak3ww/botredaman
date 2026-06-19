import sqlite3

conn = sqlite3.connect('redaman.db')
cursor = conn.cursor()

cursor.execute("UPDATE olts SET brand='GGCLINK', ip_port='192.168.30.3:8001' WHERE id=3")
cursor.execute("UPDATE olts SET brand='GGCLINK', ip_port='192.168.30.5:8002' WHERE id=4")

conn.commit()
print("Berhasil update DB")
