from scapy.all import Packet, BitField


class SwitchMLPacket(Packet):
    name = "SwitchMLPacket"
    fields_desc = [
        BitField("wid", 0, 32),
        BitField("ver", 0, 32),
        BitField("idx", 0, 32),
        BitField("offset", 0, 32),
        BitField("mgid", 0, 16),
        BitField("size", 0, 32),
        BitField("type", 0, 32)
    ]


class DataPacket(Packet):
    name = "DataPacket"
    fields_desc = [
        BitField("value00", 0, 32),
        BitField("value01", 0, 32),
        BitField("value02", 0, 32),
        BitField("value03", 0, 32),
        BitField("value04", 0, 32),
        BitField("value05", 0, 32),
        BitField("value06", 0, 32),
        BitField("value07", 0, 32),  
        BitField("value08", 0, 32),  
        BitField("value09", 0, 32),  
        BitField("value10", 0, 32),  
        BitField("value11", 0, 32),  
        BitField("value12", 0, 32),  
        BitField("value13", 0, 32),  
        BitField("value14", 0, 32),  
        BitField("value15", 0, 32),  
        BitField("value16", 0, 32),  
        BitField("value17", 0, 32),  
        BitField("value18", 0, 32),  
        BitField("value19", 0, 32),  
        BitField("value20", 0, 32),  
        BitField("value21", 0, 32),  
        BitField("value22", 0, 32),  
        BitField("value23", 0, 32),  
        BitField("value24", 0, 32),  
        BitField("value25", 0, 32),  
        BitField("value26", 0, 32),  
        BitField("value27", 0, 32),  
        BitField("value28", 0, 32),  
        BitField("value29", 0, 32),  
        BitField("value30", 0, 32),  
        BitField("value31", 0, 32) 
    ]


class SubscriptionPacket(Packet):
    name = "SubscriptionPacket"
    fields_desc = [
        BitField("rank", 0, 32),
        BitField("mgid", 0, 32),
        BitField("type", 0, 32)
    ]


class SyncPacket(Packet):
    name = "SyncPacket"
    fields_desc = [
        BitField("mgid", 0, 16),
        BitField("type", 0, 16),
        BitField("offset", 0, 32)
    ]
