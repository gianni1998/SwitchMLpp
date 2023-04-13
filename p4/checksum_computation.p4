#include "includes/headers.p4"
#include "includes/types.p4"


control TheChecksumComputation(inout headers  hdr, inout metadata meta) {
  apply {
    update_checksum(
      hdr.ipv4.isValid(), 
      { 
        hdr.ipv4.version, 
        hdr.ipv4.IHL, 
        hdr.ipv4.typeOfService, 
        hdr.ipv4.totalLenght, 
        hdr.ipv4.identification, 
        hdr.ipv4.flags, 
        hdr.ipv4.fragmentOffset, 
        hdr.ipv4.timeToLive, 
        hdr.ipv4.protocol, 
        hdr.ipv4.sourceAddress, 
        hdr.ipv4.destinationAddress
      }, 
      hdr.ipv4.headerCheckSum, 
      HashAlgorithm.csum16
    );

    update_checksum(
      hdr.sml.isValid(),
      {
        hdr.ipv4.sourceAddress,
        hdr.ipv4.destinationAddress,
        (bit<8>) 0x00,
        hdr.ipv4.protocol,
        hdr.udp.hdrlength,
        hdr.udp.srcPort,
        hdr.udp.dstPort,
        hdr.udp.hdrlength,
        hdr.sml,
        hdr.data
      },
      hdr.udp.checksum,
      HashAlgorithm.csum16
    );
  }
}