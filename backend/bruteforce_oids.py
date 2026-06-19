from pysnmp.hlapi import *

def check_oid(ip, port, community, oid):
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget((ip, port), timeout=2.0, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )
    
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator, (None, None, None, []))
    
    if errorIndication or errorStatus:
        return False
    elif len(varBinds) > 0:
        return True
    return False

if __name__ == '__main__':
    ip = '103.157.79.178'
    port = 1611
    community = 'public'
    
    print("Mencoba berbagai OID standar GPON...")
    common_oids = [
        '1.3.6.1.4.1.17409.2.3.4.2.1.4', # C-Data / VSOL GPON
        '1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15', # Huawei GPON
        '1.3.6.1.4.1.3902.1012.3.50.12.1.1.14', # ZTE GPON
        '1.3.6.1.4.1.3320.101.10.5.1.5', # BDCOM GPON
        '1.3.6.1.4.1.50308', # HSGQ Private
        '1.3.6.1.4.1.50293', # OEM Private
        '1.3.6.1.4.1.5875' # Default OEM
    ]
    
    found = False
    for oid in common_oids:
        print(f"Mencoba OID: {oid} ...")
        if check_oid(ip, port, community, oid):
            print(f"BERHASIL! OLT membalas data di jalur OID: {oid} 🎉")
            found = True
    
    if not found:
        print("Semua OID umum gagal.")
