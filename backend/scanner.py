from pysnmp.hlapi import *

def walk_olt(ip, port, community, base_oid, output_file):
    print(f"Memulai pemindaian mendalam ke {ip}:{port} pada OID {base_oid}...")
    
    with open(output_file, 'w') as f:
        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),  # v2c
            UdpTransportTarget((ip, port), timeout=3.0, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(base_oid)),
            lexicographicMode=False
        ):
            if errorIndication:
                print(f"Error: {errorIndication}")
                break
            elif errorStatus:
                print(f"Error: {errorStatus}")
                break
            else:
                for varBind in varBinds:
                    oid = varBind[0].prettyPrint()
                    val = varBind[1].prettyPrint()
                    f.write(f"{oid} = {val}\n")
    
    print(f"Pemindaian selesai! Hasil disimpan di {output_file}")

if __name__ == '__main__':
    # Kita scan branch Enterprise (1.3.6.1.4.1) untuk mencari letak data GPON
    walk_olt('103.157.79.178', 1611, 'public', '1.3.6.1.4.1', 'c:\\BotRedaman\\hsgq_scan.txt')
