#ifndef _TYPES_H
#define _TYPES_H

#define MAX_WORKERS 5

typedef bit<9>  sw_port_t;   /*< Switch port */
typedef bit<48> mac_addr_t;  /*< MAC address */
typedef bit<32> ipv4_addr_t;
typedef bit<32> sml_value_t;

const bit<32> max_chunks = 1;

enum bit<16> udp_port_t {
    sml = 54321,
    sync = 65432
}

enum bit<16> ether_type_t {
    arp = 0x806,
    ipv4 = 0x800,
    sml = 0x69
}

enum bit<16> arp_oper_t {
    REQUEST = 1,
    REPLY   = 2
}

enum bit<8> ip_protocol_t {
    tcp = 6,
    udp = 17
}

struct metadata { 
    bit<1> seen;
    bit<32> count;
    bit<32> idx;
    bit<32> numWorkers;
}

#endif