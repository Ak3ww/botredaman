from pysnmp.hlapi import *

def walk_olt(ip, port, community, filename, base_oid='1.3.6.1.4.1'):
    print(f"Walking {ip}:{port} (Community: {community}) -> {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        # Kita coba v2c dulu, kalau gagal, nanti kita coba v1
        for (errorIndication, errorStatus, errorIndex, varBinds) in bulkCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1), # v2c
            UdpTransportTarget((ip, port), timeout=3.0, retries=2),
            ContextData(),
            0, 50, # nonRepeaters, maxRepetitions
            ObjectType(ObjectIdentity(base_oid)),
            lexicographicMode=False
        ):
            if errorIndication:
                print(f"Error {ip}:{port} - {errorIndication}")
                break
            elif errorStatus:
                print(f"Error {ip}:{port} - {errorStatus}")
                break
            else:
                for varBind in varBinds:
                    f.write(f"{varBind[0]} = {varBind[1]}\n")
    print(f"Selesai {filename}")

if __name__ == "__main__":
    IP = '192.168.30.6'
    walk_olt(IP, 161, 'public', 'c:\\BotRedaman\\vsol_rx.txt', '1.3.6.1.4.1.37950.1.1.5.12.2')
