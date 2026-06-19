from pysnmp.hlapi import *

def get_snmp_walk(ip, port, community, base_oid, version=0):
    results = {}
    try:
        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=version),
            UdpTransportTarget((ip, port), timeout=3.0, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(base_oid)),
            lexicographicMode=False
        ):
            if not errorIndication and not errorStatus:
                for varBind in varBinds:
                    results[varBind[0].prettyPrint()] = varBind[1].prettyPrint()
    except Exception as e:
        print(e)
    return results

# HSGQ
print("Fetching HSGQ (103.157.79.178:1611) SN & Version info...")
data = get_snmp_walk("103.157.79.178", 1611, "public", "1.3.6.1.4.1.50224.3.12.2.1", 0)
for k, v in list(data.items())[:200]:
    if "ZTEG" in v or "HWTC" in v or "V" in v or "v" in v or len(v)>8:
        print(f"HSGQ OID: {k} = {v}")

# VSOL
print("\nFetching VSOL (192.168.30.6:161) SN & Version info...")
data = get_snmp_walk("192.168.30.6", 161, "public", "1.3.6.1.4.1.37950.1.1.6.1.1.2.1", 1)
for k, v in list(data.items())[:200]:
    if "ZTEG" in v or "HWTC" in v or "V" in v or "v" in v or len(v)>8:
        print(f"VSOL OID: {k} = {v}")
