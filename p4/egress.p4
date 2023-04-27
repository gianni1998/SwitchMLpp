#include "handlers/sml_handler.p4"


control TheEgress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

  SMLHandler() smlHandler;

  apply {
    if (hdr.sml.isValid() || hdr.sync.isValid()){
      smlHandler.apply(hdr, standard_metadata);
    }
  }
}