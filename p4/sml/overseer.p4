#ifndef _OVERSEER_H
#define _OVERSEER_H

#include "../includes/types.p4"

control Overseer(in headers hdr, 
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    register<bit<32>> (NUM_OF_WORKERS) r;

    apply {
        r.read(meta.idx, hdr.sml.wid);

        if (hdr.sml.idx == meta.idx || hdr.sml.idx + 1 == meta.idx){
            meta.seen = 1;
        } else {
            r.write(hdr.sml.wid, hdr.sml.idx);
            meta.seen = 0;
        }
    }
}

#endif