from pysnmp.hlapi import *

def walk_snmpv1(ip, port, community, base_oid, output_file):
    print(f"Memulai SNMPv1 Walk pada {base_oid}...")
    
    with open(output_file, 'w') as f:
        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0), # WAJIB SNMPv1
            UdpTransportTarget((ip, port), timeout=3.0, retries=2),
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
    
    print(f"Pemindaian selesai! Disimpan di {output_file}")

if __name__ == '__main__':
    # Enterprise ID 50224 ditemukan dari pengujian sebelumnya
    walk_snmpv1('103.157.79.178', 1611, 'public', '1.3.6.1.4.1.50224', 'c:\\BotRedaman\\gpon_walk.txt')
