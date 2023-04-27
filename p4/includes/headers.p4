#ifndef _HEADERS_H
#define _HEADERS_H

#include "types.p4"

header ethernet_t {
  mac_addr_t destinationMacAddress;
  mac_addr_t sourceMacAddress;
  ether_type_t etherType;
}

header arp_t {
    bit<16> htype;
    bit<16> ptype;
    bit<8> hlen;
    bit<8> plen;
    arp_oper_t oper;
    bit<48> sha;
    bit<32> spa;
    bit<48> tha;
    bit<32> tpa;
}

header ipv4_t {
    bit<4> version;
    bit<4> IHL;
    bit<8> typeOfService;
    bit<16> totalLenght;
    bit<16> identification;
    bit<3> flags;
    bit<13> fragmentOffset;
    bit<8> timeToLive;
    ip_protocol_t protocol;
    bit<16> headerCheckSum;
    ipv4_addr_t sourceAddress;
    ipv4_addr_t destinationAddress;
}

header udp_t {
  bit<16> srcPort;
  bit<16> dstPort;
  bit<16> hdrlength;
  bit<16> checksum;
}

header sml_t {
  bit<32> wid;
  bit<32> ver;
  bit<32> idx;
  bit<32> offset;
  bit<32> mgid;
  bit<32> size;
}

header data_t {
  sml_value_t value00;
  sml_value_t value01;
  sml_value_t value02;
  sml_value_t value03;
  sml_value_t value04;
  sml_value_t value05;
  sml_value_t value06;
  sml_value_t value07;
  sml_value_t value08;
  sml_value_t value09;
  sml_value_t value10;
  sml_value_t value11;
  sml_value_t value12;
  sml_value_t value13;
  sml_value_t value14;
  sml_value_t value15;
  sml_value_t value16;
  sml_value_t value17;
  sml_value_t value18;
  sml_value_t value19;
  sml_value_t value20;
  sml_value_t value21;
  sml_value_t value22;
  sml_value_t value23;
  sml_value_t value24;
  sml_value_t value25;
  sml_value_t value26;
  sml_value_t value27;
  sml_value_t value28;
  sml_value_t value29;
  sml_value_t value30;
  sml_value_t value31;
}

header sync_t {
  bit<32> offset;
}

struct headers {
  ethernet_t ethernet;
  arp_t arp;
  ipv4_t ipv4;
  udp_t udp;
  sml_t sml;
  data_t data;
  sync_t sync;
}

#endif