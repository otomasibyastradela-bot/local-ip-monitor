import subprocess
import platform
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 1. Setup Koneksi ke Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Buka spreadsheet berdasarkan nama
sheet_app = client.open("IP Network Monitor")
sheet_lokasi = sheet_app.worksheet("Lokasi")
sheet_status = sheet_app.worksheet("Status_IP")

def ping_ip(ip):
    """Fungsi untuk melakukan ping ke sebuah IP"""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", "-w", "1000", ip]
    reply = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return reply.returncode == 0

def run_scanner():
    print(Memulai pemindaian jaringan pada {datetime.now()}...)
    
    # Ambil data lokasi dari Google Sheets
    locations = sheet_lokasi.get_all_records()
    
    all_status_data = []
    
    for loc in locations:
        loc_id = loc['id']
        segmen = loc['segmen_ip'] # Contoh: 10.4.0.0/24
        base_ip = ".".join(segmen.split(".")[:3]) # Mengambil 10.4.0
        
        print(Memindai Stasiun: {loc['nama_lokasi']} ({segmen})...)
        
        # Simulasi scan 10 IP pertama di segmen tersebut (bisa disesuaikan)
        for i in range(1, 15):
            target_ip = f"{base_ip}.{i}"
            is_active = ping_ip(target_ip)
            status_text = "Aktif" if is_active else "Tidak Aktif"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            all_status_data.append([target_ip, loc_id, status_text, timestamp])

    # Update hasilnya ke Tab Status_IP di Google Sheets
    # Clear data lama, tulis data baru
    sheet_status.clear()
    sheet_status.append_row(["ip", "lokasi_id", "status", "last_update"])
    for row in all_status_data:
        sheet_status.append_row(row)
        
    print("Pemindaian selesai dan data berhasil disinkronkan ke Google Sheets!")

if __name__ == "__main__":
    run_scanner()