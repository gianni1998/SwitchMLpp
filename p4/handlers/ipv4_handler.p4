#ifndef _IPV4_HANDLER_H
#define _IPV4_HANDLER_H

#include "../includes/headers.p4"
#include "../includes/types.p4"

control IPv4Handler(inout headers hdr, 
                    inout standard_metadata_t standard_metadata) {

    action forward(mac_addr_t destinationAddress, sw_port_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.sourceMacAddress = hdr.ethernet.destinationMacAddress;
        hdr.ethernet.destinationMacAddress = destinationAddress;
        hdr.ipv4.timeToLive = hdr.ipv4.timeToLive - 1;
    }

    table handler {
        key = { hdr.ipv4.destinationAddress: lpm; }
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