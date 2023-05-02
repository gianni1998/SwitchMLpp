#ifndef _ARP_HANDLER_H
#define _ARP_HANDLER_H

#include "../includes/headers.p4"
#include "../includes/types.p4"

control ARPHandler(inout headers hdr, 
                   inout standard_metadata_t standard_metadata) {

    action forward(mac_addr_t switch_mac) {
        ipv4_addr_t switch_ip = hdr.arp.tpa;
        hdr.arp.oper = arp_oper_t.REPLY;
        hdr.arp.tha = hdr.arp.sha;
        hdr.arp.tpa = hdr.arp.spa;
        hdr.arp.sha = switch_mac;
        hdr.arp.spa = switch_ip;

        standard_metadata.egress_spec = standard_metadata.ingress_port;
    }

    table handler {
        key = { hdr.arp.tpa: exact; }
        actions = {
            forward;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        handler.apply();
    }
}

#endif