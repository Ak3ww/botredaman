import telnetlib
import time

def test_telnet(ip, port, user, password):
    print(f"Connecting to {ip}:{port}...")
    try:
        tn = telnetlib.Telnet(ip, port, timeout=5)
        
        # Baca layar login
        output = tn.read_until(b"name:", timeout=5)
        print("Received:", output.decode('utf-8', errors='ignore'))
        
        # Kirim username
        tn.write(user.encode('ascii') + b"\n")
        
        # Baca layar password
        output = tn.read_until(b"word:", timeout=5)
        print("Received:", output.decode('utf-8', errors='ignore'))
        
        # Kirim password
        tn.write(password.encode('ascii') + b"\n")
        
        time.sleep(2)
        output = tn.read_very_eager()
        print("Login Output:", output.decode('utf-8', errors='ignore'))
        
        # Kirim command untuk mengecek snmp
        tn.write(b"enable\n")
        time.sleep(1)
        tn.write(b"show snmp-server\n")
        time.sleep(1)
        
        output = tn.read_very_eager()
        print("Command Output:", output.decode('utf-8', errors='ignore'))
        
        tn.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_telnet("192.168.30.6", 23, "euginemedia", "#eugine0909")
