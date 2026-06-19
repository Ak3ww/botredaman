from pysnmp.hlapi import *

def test_snmp_v1(ip, port, community):
    print(f"Menguji SNMP v1 pada {ip}:{port}...")
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0), # mpModel=0 adalah SNMPv1
        UdpTransportTarget((ip, port), timeout=3.0, retries=2),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.1.2.0')) # sysObjectID
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        print(f"Error SNMPv1: {errorIndication}")
    elif errorStatus:
        print(f"Error Status: {errorStatus}")
    else:
        for varBind in varBinds:
            print(f"BERHASIL SNMPv1! {varBind[0]} = {varBind[1].prettyPrint()}")

if __name__ == '__main__':
    test_snmp_v1('103.157.79.178', 1611, 'public')
