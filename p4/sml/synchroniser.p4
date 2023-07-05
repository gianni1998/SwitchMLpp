#ifndef _SYNCHRONISER_H
#define _SYNCHRONISER_H

#include "../includes/types.p4"

control Synchroniser(inout headers hdr, 
                     in bit<1> sync) {

    register<bit<32>> (1) r;
    bit<32> value;

    apply {
        @atomic{
            r.read(value, 0);

            if (sync == 1) {
                hdr.sync.offset = value;
            } else if (hdr.sml.offset > value || hdr.sml.offset + CHUNK_THRESHOLD < value) {
                r.write(0, hdr.sml.offset);
            }
        }
    }
}

#endif