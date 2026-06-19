import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pysnmp.hlapi import *

def test_snmp(ip, port, community='public'):
    print(f"\nMencoba menghubungi {ip}:{port} menggunakan SNMP (Community: {community})...")
    
    sysDescr_OID = '1.3.6.1.2.1.1.1.0'
    
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1), # mpModel=1 means SNMPv2c
            UdpTransportTarget((ip, int(port)), timeout=3.0, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(sysDescr_OID))
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            print(f"❌ GAGAL: {errorIndication}")
            print("Penyebab mungkin: SNMP di OLT belum aktif, Community bukan 'public', atau Port salah/terblokir firewall.")
        elif errorStatus:
            print(f"❌ GAGAL: {errorStatus.prettyPrint()}")
        else:
            print("✅ BERHASIL TERHUBUNG!")
            for varBind in varBinds:
                print(f"Informasi OLT: {varBind[1].prettyPrint()}")
            print("\nKesimpulan: SNMP aktif dan bisa kita gunakan untuk menyedot data redaman!")

    except Exception as e:
        print(f"Terjadi kesalahan sistem: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Penggunaan: python snmp_tester.py <IP> <PORT>")
        sys.exit(1)
    ip_address = sys.argv[1]
    port = sys.argv[2]
    test_snmp(ip_address, port)
