from scapy.all import Packet, BitField


class Data(Packet):
    name = "DataPacket"
    fields_desc = [
        BitField("value0", 0, 32),
        BitField("value1", 0, 32),
        BitField("value2", 0, 32),
        BitField("value3", 0, 32),
        BitField("value4", 0, 32),
        BitField("value5", 0, 32),
        BitField("value6", 0, 32),
        BitField("value7", 0, 32),  
        BitField("value8", 0, 32),  
        BitField("value9", 0, 32),  
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