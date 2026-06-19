from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import uvicorn
import os

app = FastAPI(title="BotRedaman NOC API")

# Setup CORS untuk frontend lokal
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Buka untuk localhost frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = 'redaman.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/olts")
def get_olts():
    conn = get_db_connection()
    olts = conn.execute('SELECT * FROM olts').fetchall()
    conn.close()
    return [dict(ix) for ix in olts]

@app.get("/api/attenuations")
def get_attenuations():
    conn = get_db_connection()
    # Mengambil data redaman terbaru
    data = conn.execute('''
        SELECT a.port_name, a.onu_id, a.customer_name, a.rx_power, a.tx_power, a.timestamp, o.name as olt_name 
        FROM attenuations a
        JOIN olts o ON a.olt_id = o.id
        ORDER BY a.timestamp DESC LIMIT 100
    ''').fetchall()
    conn.close()
    return [dict(ix) for ix in data]

@app.get("/api/chart_data")
def get_chart_data(onu_id: str):
    conn = get_db_connection()
    data = conn.execute('''
        SELECT rx_power, timestamp 
        FROM attenuations 
        WHERE onu_id = ?
        ORDER BY timestamp ASC LIMIT 50
    ''', (onu_id,)).fetchall()
    conn.close()
    return [dict(ix) for ix in data]

# Serve React App
dist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")
if os.path.exists(os.path.join(dist_path, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

@app.get("/")
def serve_dashboard():
    return FileResponse(os.path.join(dist_path, "index.html"))

if __name__ == "__main__":
    print("Memulai server API BotRedaman di port 8000...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
