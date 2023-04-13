from scapy.all import Packet, BitField


class SwitchML(Packet):
    name = "SwitchMLPacket"
    fields_desc = [
        BitField("wid", 0, 32),
        BitField("ver", 0, 32),
        BitField("idx", 0, 32),
        BitField("offset", 0, 32),
        BitField("size", 0, 32)
    ]