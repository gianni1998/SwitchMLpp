from python.lib.p4app.src.p4_mininet import P4RuntimeSwitch

NUM_WORKERS = {"table": "TheIngress.num_workers", "action" : "TheIngress.set_num_workers"}
SML = {"table": "TheEgress.sml_handler", "action": "TheEgress.sml_forward"}
NEXT_STEP = {"table": "TheIngress.next_step", "action": "TheIngress.set_next_step"}


def num_workers_entry(conn: P4RuntimeSwitch, mgid: int, num: int, insert: bool) -> None:
    """
    Insert or remove a Number of workers table entry on the switch
    @param conn: Connection to the switch
    @param mgid: Multicast group id
    @param num: The number of workers
    @param insert: Boolean value that decides to inserted or remove the entry
    """
    match = {"meta.mgid": mgid}
    params = {"num_workers": num}

    send_entry(conn=conn, table_info=NUM_WORKERS, match=match, params=params, insert=insert)


def sml_entry(conn: P4RuntimeSwitch, port: int, mac: str, ip: str, insert: bool) -> None:
    """
    Insert or remove a SwitchML table entry on the switch
    @param conn: Connection to the switch
    @param port: Port number of the SML entry
    @param mac: MAC address of the SML entry
    @param ip: IP address of the SML entry
    @param insert: Boolean value that decides to inserted or remove the entry
    """
    match = {"standard_metadata.egress_port": port}
    params = {"worker_mac": mac, "worker_ip": ip}

    send_entry(conn=conn, table_info=SML, match=match, params=params, insert=insert)


def next_step_entry(conn: P4RuntimeSwitch, mgid: int, step: int, port: int, insert: bool) -> None:
    """
    Insert or remove a Next step table entry on the switch
    @param conn: Connection to the switch
    @param mgid: Multicast group id
    @param step: Next step value
    @param insert: Boolean value that decides to inserted or remove the entry
    """
    match = {"meta.mgid": mgid}
    params = {"step": step, "port": port}

    send_entry(conn=conn, table_info=NEXT_STEP, match=match, params=params, insert=insert)


def send_entry(conn: P4RuntimeSwitch, table_info: dict, match: dict, params: dict, insert: bool) -> None:
    """
    Generic method for inserting and removing table entries of a switch
    @param conn: Connection to the switch
    @param table_info: Dictionary holding the table name and action name
    @param match: Match fields of the table entry
    @param params: Parameters of the table entry
    @param insert: Boolean value that decides to inserted or remove the entry
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