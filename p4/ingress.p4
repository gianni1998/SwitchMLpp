#include "handlers/ipv4_handler.p4"
#include "handlers/arp_handler.p4"
#include "handlers/aggregation_handler.p4"

#include "sml/worker_counter.p4"
#include "sml/overseer.p4"
#include "sml/synchroniser.p4"

control TheIngress(inout headers hdr,
                   inout metadata meta,
                   inout standard_metadata_t standard_metadata) {

  IPv4Handler() ipv4Handler;
  ARPHandler() arpHandler;
  AggregationHandler() aggregationHandler;

  Overseer() overseer;
  WorkerCounter() workerCounter;
  Synchroniser() syncer;

  action multicast() {
    standard_metadata.mcast_grp = hdr.sml.mgid;
    hdr.sml.type = 1;
  }

  action reply() {
    standard_metadata.egress_spec = standard_metadata.ingress_port;
  }

  action send_to_next_switch() {
    standard_metadata.egress_spec = meta.nextStepPort;
  }

  action drop() {
    mark_to_drop(standard_metadata);
  }

  action set_switch_mac_and_ip(mac_addr_t switch_mac, ipv4_addr_t switch_ip) {
    hdr.ethernet.sourceMacAddress = switch_mac;
    hdr.ipv4.sourceAddress = switch_ip;
  }

  action set_num_workers(bit<32> num_workers) {
    meta.numWorkers = num_workers;
  }

  action set_switch_rank(bit<32> rank) {
    hdr.sml.wid = rank;
  }

  action set_next_step(bit<1> step, bit<9> port) {
    meta.nextStep = step; // 1 send up; 0 send down
    meta.nextStepPort = port;
  }

  table switch_mac_and_ip {
    actions = { @defaultonly set_switch_mac_and_ip; }
    size = 1;
  }

  table num_workers {
    key = { hdr.sml.mgid: exact; }
    actions = {
      set_num_workers;
      reply;
    }
    size = 1024;
    default_action = reply();
  }

  table next_step {
    key = { hdr.sml.mgid: exact; }
    actions = {
      set_next_step;
      NoAction;
    }
    size = 1024;
    default_action = NoAction();
  }

  table switch_rank {
    actions = { @defaultonly set_switch_rank; }
    size = 1;
  }

  table debug {
    key = { hdr.sml.idx: exact;
            standard_metadata.ingress_port: exact;
            meta.count: exact; 
            hdr.sml.wid: exact; }
    actions = { @defaultonly NoAction; }
    size = 1;
  }

  apply {

    if (hdr.arp.isValid()) {
      arpHandler.apply(hdr, standard_metadata);

    } else if (hdr.ipv4.isValid()) {

      if (hdr.sml.isValid()) {
        bit<32> idx = 0;

        // Get number of workers in group
        num_workers.apply();

        // Save offset in register for sync
        syncer.apply(hdr, 0);

        // Get next step
        next_step.apply();

        @atomic {
          // Check if packet is duplicate
          if (hdr.sml.type == 0) {
            overseer.apply(hdr, meta, standard_metadata);
          } else {
            meta.seen = 0;
          }

          // Count worker if not seen or reset counter
          workerCounter.apply(hdr, meta, idx);
        }

        debug.apply();

        if (hdr.sml.type == 1) {
          // Reply from switch, so send down
          multicast();

          standard_metadata.egress_spec = 1;

          // Manupulate values to override local agg values
          meta.count = 1;
        }

        // Do aggregation logic
        aggregationHandler.apply(hdr, meta, idx);

        // Set switch rank
        switch_rank.apply();

        if (hdr.sml.type == 0) {

          if (meta.count == 0) {
            if (meta.seen == 0) {
              // All chunks have been aggregated
              multicast();
            } else {
              // Worker hasn't received chuck so resend
              reply();
            }
          } else if (meta.count == meta.numWorkers && meta.nextStep == 1 && meta.seen == 0) {
            send_to_next_switch();
          } else {
            // Packet is duplicate or chunk is not ready, so drop
            drop();
          }
        }

      } else if (hdr.sync.isValid()) {
        syncer.apply(hdr, 1);
        reply();

      } else {
        ipv4Handler.apply(hdr, standard_metadata);
      }

      if (hdr.sync.isValid() || hdr.sml.isValid()) {
        switch_mac_and_ip.apply();
      }
    }
  }
}