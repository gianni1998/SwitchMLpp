#ifndef _SML_HANDLER_H
#define _SML_HANDLER_H

#include "../includes/headers.p4"
#include "../includes/types.p4"

control SMLHandler(inout headers hdr, 
                   inout standard_metadata_t standard_metadata) {

    action forward(mac_addr_t worker_mac, ipv4_addr_t worker_ip) {
        hdr.ethernet.destinationMacAddress = worker_mac;
        hdr.ipv4.destinationAddress = worker_ip;
        hdr.ipv4.timeToLive = hdr.ipv4.timeToLive - 1;     
    }

    table handler {
        key = { standard_metadata.egress_port : exact; }
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