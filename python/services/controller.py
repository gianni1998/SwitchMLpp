from python.lib.p4app.src.p4_mininet import P4RuntimeSwitch

from python.models.switch import SwitchConnectionInfo


NUM_WORKERS = {"table": "TheIngress.num_workers", "action" : "TheIngress.set_num_workers"}
SML = {"table": "TheEgress.sml_handler", "action": "TheEgress.sml_forward"}


def create_entries(info: SwitchConnectionInfo, mgid: int, port: int, ip: str, mac: str) -> None:
    """
    Method for creating the SML table entries in a switch
    """
    # Multicast
    info.mgids.append(mgid)
    info.mg_ports[mgid] = [port]
    info.connection.addMulticastGroup(mgid=mgid, ports=info.mg_ports[mgid])

    # Number of workers
    num_workers_entry(conn=info.connection, mgid=mgid, num=len(info.mg_ports[mgid]), insert=True)

    # SwitchML
    info.connected_ip.append(ip)
    sml_entry(conn=info.connection, port=port, mac=mac, ip=ip, insert=True)


def update_entries(info: SwitchConnectionInfo, mgid: int, port: int, ip: str, mac: str) -> None:
    """
    Method for updating the SML table entries in a switch
    """
    if ip not in info.connected_ip:
        # Multicast group
        info.mg_ports[mgid].append(port)
        info.connection.updateMulticastGroup(mgid=mgid, ports=info.mg_ports[mgid])

        # Number of Workers
        num_workers_entry(conn=info.connection, mgid=mgid, num=len(info.mg_ports[mgid])-1, insert=False)
        num_workers_entry(conn=info.connection, mgid=mgid, num=len(info.mg_ports[mgid]), insert=True)

        # SwitchML
        info.connected_ip.append(ip)
        sml_entry(conn=info.connection, port=port, mac=mac, ip=ip, insert=True)


def delete_entries(info: SwitchConnectionInfo, mgid: int, port: int, ip: str, mac: str) -> None:
    """
    Method to delete the SML table entries in a switch
    """
    if mgid in info.mgids and port in info.mg_ports[mgid]:

        if len(info.mg_ports[mgid]) > 1:
            # Multicast group
            info.mg_ports[mgid].remove(port)
            info.connection.updateMulticastGroup(mgid=mgid, ports=info.mg_ports[mgid])

            # Number of Workers
            num_workers_entry(conn=info.connection, mgid=mgid, num=len(info.mg_ports[mgid])+1, insert=False)
            num_workers_entry(conn=info.connection, mgid=mgid, num=len(info.mg_ports[mgid]), insert=True)
        
        else:
            # Multicast group
            info.connection.deleteMulticastGroup(mgid=mgid, ports=[])
            info.mgids.remove(mgid)
            del info.mg_ports[mgid]

            # Number of workers
            num_workers_entry(conn=info.connection, mgid=mgid, num=1, insert=False)
        
        # SwitchML
        info.connected_ip.remove(ip)
        sml_entry(conn=info.connection, port=port, mac=mac, ip=ip, insert=False)


def num_workers_entry(conn: P4RuntimeSwitch, mgid: int, num: int, insert: bool) -> None:
    """
    Method to send a number of workers entry action to the switch
    """
    match = {"hdr.sml.mgid": mgid}
    params = {"num_workers": num}

    send_entry(conn=conn, table_info=NUM_WORKERS, match=match, params=params, insert=insert)


def sml_entry(conn: P4RuntimeSwitch, port: int, mac: str, ip: str, insert: bool) -> None:
    """
    Method to send a SML forward entry action to the switch
    """
    match = {"standard_metadata.egress_port": port}
    params = {"worker_mac": mac, "worker_ip": ip}

    send_entry(conn=conn, table_info=SML, match=match, params=params, insert=insert)


def send_entry(conn: P4RuntimeSwitch, table_info: dict, match: dict, params: dict, insert: bool) -> None:
    """
    Generic method for inserting and removing table entries of a switch
    """
    if insert:
        conn.insertTableEntry(
            table_name=table_info["table"],
            match_fields=match,
            action_name=table_info["action"],
            action_params=params
        )
    else:
        conn.removeTableEntry(
            table_name=table_info["table"],
            match_fields=match,
            action_name=table_info["action"],
            action_params=params
        )