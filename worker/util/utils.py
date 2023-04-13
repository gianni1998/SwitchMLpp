from scapy.all import raw
from lib.worker import Log

from util.constants import CHUNK_SIZE, SWITCH_ML_PACKET_SIZE
from packets.data_packet import Data
from packets.switchml_packet import SwitchML


def packet_builder(wid, ver, idx, offset, vector):
    data = [0] * 32
    data[:CHUNK_SIZE] = vector

    sml = SwitchML(wid=wid, ver=ver, idx=idx, offset=offset, size=CHUNK_SIZE)
    data = Data(value0=data[0], value1=data[1], value2=data[2], value3=data[3], 
                value4=data[4], value5=data[5], value6=data[6], value7=data[7],
                value8=data[8], value9=data[9], value10=data[10], value11=data[11],
                value12=data[12], value13=data[13], value14=data[14], value15=data[15],
                value16=data[16], value17=data[17], value18=data[18], value19=data[19],
                value20=data[20], value21=data[21], value22=data[22], value23=data[23],
                value24=data[24], value25=data[25], value26=data[26], value27=data[27],
                value28=data[28], value29=data[29], value30=data[30], value31=data[31])
    
    return raw(sml / data)


def packet_parser(packet, result):
    load = packet[-(CHUNK_SIZE*4+SWITCH_ML_PACKET_SIZE):]

    ver = int.from_bytes(load[4:8], byteorder="big")
    idx = int.from_bytes(load[8:12], byteorder="big")
    offset = int.from_bytes(load[12:16], byteorder="big")
    size = int.from_bytes(load[16:20], byteorder="big")
    res = [int.from_bytes(load[i:i+4], byteorder="big") for i in range(SWITCH_ML_PACKET_SIZE, len(load), 4)]

    Log(f"Chuncky: {idx}, VER: {ver}")
    result[offset:offset + size] = res[:size]

    offset += CHUNK_SIZE
    idx += 1
    ver = (ver+1)%2

    return offset, idx, ver
