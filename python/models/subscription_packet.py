from scapy.all import Packet, BitField


class Subscription(Packet):
    name = "SwitchMLPacket"
    fields_desc = [
        BitField("ip", 0, 32),
        BitField("type", 0, 32),
    ]