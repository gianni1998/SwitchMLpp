
control TheEgress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

  action sml_forward(mac_addr_t worker_mac, ipv4_addr_t worker_ip) {
    hdr.ethernet.destinationMacAddress = worker_mac;
    hdr.ipv4.destinationAddress = worker_ip;
    hdr.ipv4.timeToLive = hdr.ipv4.timeToLive - 1;     
  }

  table sml_handler {
    key = { standard_metadata.egress_port : exact; }
    actions = {
      sml_forward;
      NoAction;
    }
    size = 1024;
    default_action = NoAction();
  }

  apply {
    if (hdr.sml.isValid() || hdr.sync.isValid()){
      sml_handler.apply();
    }
  }
}