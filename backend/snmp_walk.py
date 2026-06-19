import sys
from pysnmp.hlapi import *

def check_rx_power(ip, port, community='public'):
    print(f"Mencoba membaca Redaman (RX Power) dari {ip}:{port}...")
    # OID untuk RX Power ONU (HSGQ/C-Data)
    rx_oid = '1.3.6.1.4.1.3320.101.108.1.3'
    
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget((ip, int(port)), timeout=5.0, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(rx_oid)),
        lexicographicMode=False
    )

    found = False
    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication or errorStatus:
            print(f"Error: {errorIndication or errorStatus}")
            break
        
        found = True
        for varBind in varBinds:
            oid_str = str(varBind[0])
            value = int(varBind[1])
            # Redaman biasanya dalam format integer (misal -231 berarti -23.1 dBm)
            dbm = value / 10.0 if value < 0 else value
            print(f"ONU {oid_str.replace(rx_oid+'.', '')} -> {dbm} dBm")

    if not found:
        print("Tidak ada data ONU ditemukan di OID ini. Mungkin port OLT kosong atau OID berbeda.")

if __name__ == '__main__':
    check_rx_power('103.157.79.178', 1611)
