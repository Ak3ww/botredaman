from pysnmp.hlapi import *

def get_sys_object_id(ip, port, community):
    print(f"Mengambil sysObjectID dari {ip}:{port}...")
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget((ip, port), timeout=5.0, retries=2),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.1.2.0'))
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        print(f"Error: {errorIndication}")
    elif errorStatus:
        print(f"Error: {errorStatus}")
    else:
        for varBind in varBinds:
            print(f"{varBind[0]} = {varBind[1].prettyPrint()}")

if __name__ == '__main__':
    get_sys_object_id('103.157.79.178', 1611, 'public')
