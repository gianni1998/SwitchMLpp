#ifndef _AGGREGATOR_H
#define _AGGREGATOR_H

control Aggregator(inout sml_value_t value, in bit<32> idx, in bit<32> ver, inout metadata meta) {

    register<sml_value_t> (max_chunks) r0;
    register<sml_value_t> (max_chunks) r1;
    sml_value_t savedValue;

    apply {
        @atomic {
            if (ver == 0) {
                r0.read(savedValue, idx);

                if (meta.seen == 0) {
                    if (meta.count != 1) {
                        value = value + savedValue;
                    }

                    r0.write(idx, value);
                } else {
                    value = savedValue;
                }
            } else {
                r1.read(savedValue, idx);

                if (meta.seen == 0) {
                    if (meta.count != 1) {
                        value = value + savedValue;
                    }

                    r1.write(idx, value);
                } else {
                    value = savedValue;
                }
            }
        }
    }
}

#endif