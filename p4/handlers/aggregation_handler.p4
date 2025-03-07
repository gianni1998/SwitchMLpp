#ifndef _AGGREGATION_HANDLER_H
#define _AGGREGATION_HANDLER_H

#include "../includes/headers.p4"
#include "../includes/types.p4"

#include "../sml/aggregator.p4"

control AggregationHandler(inout headers hdr, 
                   inout metadata meta,
                   in bit<32> idx) {

    Aggregator() aggValue00;
    Aggregator() aggValue01;
    Aggregator() aggValue02;
    Aggregator() aggValue03;
    Aggregator() aggValue04;
    Aggregator() aggValue05;
    Aggregator() aggValue06;
    Aggregator() aggValue07;
    Aggregator() aggValue08;
    Aggregator() aggValue09;
    Aggregator() aggValue10;
    Aggregator() aggValue11;
    Aggregator() aggValue12;
    Aggregator() aggValue13;
    Aggregator() aggValue14;
    Aggregator() aggValue15;
    Aggregator() aggValue16;
    Aggregator() aggValue17;
    Aggregator() aggValue18;
    Aggregator() aggValue19;
    Aggregator() aggValue20;
    Aggregator() aggValue21;
    Aggregator() aggValue22;
    Aggregator() aggValue23;
    Aggregator() aggValue24;
    Aggregator() aggValue25;
    Aggregator() aggValue26;
    Aggregator() aggValue27;
    Aggregator() aggValue28;
    Aggregator() aggValue29;
    Aggregator() aggValue30;
    Aggregator() aggValue31;

    apply {
        aggValue00.apply(hdr.data.value00, idx, hdr.sml.ver, meta);
        aggValue01.apply(hdr.data.value01, idx, hdr.sml.ver, meta);
        aggValue02.apply(hdr.data.value02, idx, hdr.sml.ver, meta);
        aggValue03.apply(hdr.data.value03, idx, hdr.sml.ver, meta);
        aggValue04.apply(hdr.data.value04, idx, hdr.sml.ver, meta);
        aggValue05.apply(hdr.data.value05, idx, hdr.sml.ver, meta);
        aggValue06.apply(hdr.data.value06, idx, hdr.sml.ver, meta);
        aggValue07.apply(hdr.data.value07, idx, hdr.sml.ver, meta);
        aggValue08.apply(hdr.data.value08, idx, hdr.sml.ver, meta);
        aggValue09.apply(hdr.data.value09, idx, hdr.sml.ver, meta);
        aggValue10.apply(hdr.data.value10, idx, hdr.sml.ver, meta);
        aggValue11.apply(hdr.data.value11, idx, hdr.sml.ver, meta);
        aggValue12.apply(hdr.data.value12, idx, hdr.sml.ver, meta);
        aggValue13.apply(hdr.data.value13, idx, hdr.sml.ver, meta);
        aggValue14.apply(hdr.data.value14, idx, hdr.sml.ver, meta);
        aggValue15.apply(hdr.data.value15, idx, hdr.sml.ver, meta);
        aggValue16.apply(hdr.data.value16, idx, hdr.sml.ver, meta);
        aggValue17.apply(hdr.data.value17, idx, hdr.sml.ver, meta);
        aggValue18.apply(hdr.data.value18, idx, hdr.sml.ver, meta);
        aggValue19.apply(hdr.data.value19, idx, hdr.sml.ver, meta);
        aggValue20.apply(hdr.data.value20, idx, hdr.sml.ver, meta);
        aggValue21.apply(hdr.data.value21, idx, hdr.sml.ver, meta);
        aggValue22.apply(hdr.data.value22, idx, hdr.sml.ver, meta);
        aggValue23.apply(hdr.data.value23, idx, hdr.sml.ver, meta);
        aggValue24.apply(hdr.data.value24, idx, hdr.sml.ver, meta);
        aggValue25.apply(hdr.data.value25, idx, hdr.sml.ver, meta);
        aggValue26.apply(hdr.data.value26, idx, hdr.sml.ver, meta);
        aggValue27.apply(hdr.data.value27, idx, hdr.sml.ver, meta);
        aggValue28.apply(hdr.data.value28, idx, hdr.sml.ver, meta);
        aggValue29.apply(hdr.data.value29, idx, hdr.sml.ver, meta);
        aggValue30.apply(hdr.data.value30, idx, hdr.sml.ver, meta);
        aggValue31.apply(hdr.data.value31, idx, hdr.sml.ver, meta);
    }
}

#endif