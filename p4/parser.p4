#include "includes/headers.p4"
#include "includes/types.p4"


parser TheParser(packet_in packet,
                 out headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

  state start {
    transition parseEthernet;
  }

  state parseEthernet {
    packet.extract(hdr.ethernet);

    transition select(hdr.ethernet.etherType) {
      ether_type_t.arp: parseArp;
      ether_type_t.ipv4: parseIPv4; 
      default: accept; 
    } 
  }

  state parseIPv4 {
    packet.extract(hdr.ipv4);
    transition select(hdr.ipv4.protocol) {
      ip_protocol_t.udp: parseUdp;
      default: accept;
    }
  }

  state parseArp {
    packet.extract(hdr.arp);
    transition accept;
  }

  state parseUdp { 
    packet.extract(hdr.udp);
    transition select(hdr.udp.dstPort) {
      sml_udp_port: parseSML;
      default: accept; 
    }
  }

  state parseSML {
    packet.extract(hdr.sml);
    transition parseData;
  }

  state parseData {
    packet.extract(hdr.data);
    transition accept;
  }
}