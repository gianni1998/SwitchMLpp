#ifndef _WORKER_COUNTER_H
#define _WORKER_COUNTER_H

#include "../includes/types.p4"
#include "../includes/headers.p4"

control WorkerCounter (inout headers hdr, 
                       inout metadata meta, 
                       in bit<32> idx) {

    register<bit<32>> (max_chunks) r0;
    register<bit<32>> (max_chunks) r1;

    apply {
        if (hdr.sml.ver == 0) {
            r0.read(meta.count, idx);
        
            if (meta.seen == 0) {
                meta.count = meta.count + 1;

                if (meta.count == NUM_OF_WORKERS) {
                    meta.count = 0;
                }

                r0.write(idx, meta.count);
            }
        } else {
            r1.read(meta.count, idx);
        
            if (meta.seen == 0) {
                meta.count = meta.count + 1;

                if (meta.count == NUM_OF_WORKERS) {
                    meta.count = 0;
                }

                r1.write(idx, meta.count);
            }
        }
    }
}

#endif