#include <core.p4>
#include <v1model.p4>

#include "parser.p4"
#include "ingress.p4"
#include "egress.p4"
#include "checksum_verification.p4"
#include "checksum_computation.p4"
#include "deparser.p4"


V1Switch(
  TheParser(),
  TheChecksumVerification(),
  TheIngress(),
  TheEgress(),
  TheChecksumComputation(),
  TheDeparser()
) main;