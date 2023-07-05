#ifndef _SYNC_HANDLER_H
#define _SYNC_HANDLER_H

#include "../includes/headers.p4"
#include "../includes/types.p4"

control SyncHandler(inout headers hdr, 
                    inout standard_metadata_t standard_metadata,
                    inout metadata meta) {
    
    action send_to_next_switch() {
        standard_metadata.egress_spec = meta.nextStepPort;
    }

    action reply() {
        ipv4_addr_t temp = hdr.ipv4.sourceAddress;
        hdr.ipv4.sourceAddress = hdr.ipv4.destinationAddress;
        hdr.ipv4.destinationAddress = temp;
        standard_metadata.egress_spec = standard_metadata.ingress_port;
    }

    register<bit<32>> (1) countR;
    register<bit<1>> (MAX_WORKERS) seenR;

    bit<32> count;
    bit<1> seen;

    apply {
        @atomic {
            if (meta.nextStep == 1) {
                send_to_next_switch();
            } else {

                countR.read(count, 1);
                seenR.read(seen, hdr.sync.rank);

                if (seen == 0) {
                    seenR.write(hdr.sync.rank, 1);
                    count = count + 1;

                    if (meta.numWorkers == count) {
                        count = 0;
                    }

                    countR.write(1, count);
                }

                if (meta.numWorkers != 1 && count != 0 && hdr.sync.offset == 0) {
                    hdr.sync.type = 1;
                } else {
                    hdr.sync.type = 2;
                }

                reply();
            }
        }
    }
}

#endif