#include "includes/headers.p4"
#include "includes/types.p4"

control TheDeparser(packet_out packet, in headers hdr) {
  apply {
    /* TODO: Implement me */
    packet.emit(hdr.ethernet);
    packet.emit(hdr.arp);
    packet.emit(hdr.ipv4);
    packet.emit(hdr.udp);
    packet.emit(hdr.sml);
    packet.emit(hdr.data);
  }
}