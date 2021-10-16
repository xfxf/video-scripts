"""
gdp.py - gstreamer data protocol
Copyright 2021 Michael Farrell <micolous+git@gmail.com>


"""

import asyncio
import binascii
import dataclasses
from enum import IntFlag, IntEnum
import time
from struct import Struct
from typing import Optional

# https://github.com/GStreamer/gst-plugins-bad/blob/master/gst/gdp/dataprotocol.c
# https://github.com/GStreamer/gst-plugins-bad/blob/master/gst/gdp/dataprotocol.h
# https://github.com/GStreamer/gstreamer/blob/master/docs/images/gdp-header.png
# fields are big endian

_GST_MINI_OBJECT_FLAG_LAST = 1 << 4
_GST_EVENT_NUM_SHIFT = 8
_CRC_INITIAL = 0xffff

class EventTypeFlags(IntFlag):
    UPSTREAM = 1 << 0
    DOWNSTREAM = 1 << 1
    SERIALIZED = 1 << 2
    STICKY = 1 << 3
    STICKY_MULTI = 1 << 4

EVENT_TYPE_BOTH = EventTypeFlags.UPSTREAM | EventTypeFlags.DOWNSTREAM


def _make_event_type(num: int, flags: EventTypeFlags) -> int:
    return ((num << _GST_EVENT_NUM_SHIFT) | int(flags)) + 64


class PayloadType(IntEnum):
    NONE = 0
    BUFFER = 1
    CAPS = 2
    EVENT_NONE = 64

    EVENT_STREAM_START = _make_event_type(40, EventTypeFlags.DOWNSTREAM | EventTypeFlags.SERIALIZED | EventTypeFlags.STICKY)
    EVENT_SEGMENT = _make_event_type(70, EventTypeFlags.DOWNSTREAM | EventTypeFlags.SERIALIZED | EventTypeFlags.STICKY)


class HeaderFlag(IntFlag):
    CRC_HEADER = 1 << 0
    CRC_PAYLOAD = 1 << 1


class BufferFlag(IntFlag):
    # Subset of GstBufferFlags
    LIVE = _GST_MINI_OBJECT_FLAG_LAST << 0
    DISCONT = _GST_MINI_OBJECT_FLAG_LAST << 2
    HEADER = _GST_MINI_OBJECT_FLAG_LAST << 6
    GAP = _GST_MINI_OBJECT_FLAG_LAST << 7
    DELTA_UNIT = _GST_MINI_OBJECT_FLAG_LAST << 9


_GDP_STRUCT = Struct('>BBB1x HL QQQQ H Q6x HH')
assert _GDP_STRUCT.size == 62, f'{_GDP_STRUCT.size}'

@dataclasses.dataclass
class GdpHeader:
    version_major: int  # uint8
    version_minor: int  # uint8
    flags: HeaderFlag  # uint8
    # 1 padding byte

    typ: PayloadType  # uint16
    length: int  # uint32

    pts: int  # uint64 nanosec
    duration: int  # uint64 nanosec
    # Source file offsets
    offset: int  # uint64, -1 = unknown
    offset_end: int  # uint64

    buffer_flags: BufferFlag  # uint16

    # ABI bytes (14)
    # gstreamer 1.x
    # decoding timestamp
    dts: int  # uint64 nanosec
    # 6 padding bytes

    # CRC16 of first 58 bytes, or 0 if ~FLAG_CRC_HEADER
    header_crc: int  # uint16

    # CRC16 of payload, or 0 if ~FLAG_CRC_PAYLOAD
    payload_crc: int  # uint16

    @classmethod
    def from_tuple(cls, a):
        a = list(a)
        a[2] = HeaderFlag(a[2])
        a[3] = PayloadType(a[3])
        a[9] = BufferFlag(a[9])
        return cls(*a)

    @classmethod
    def unpack_from(cls, buffer, offset: int = 0):
        return cls.from_tuple(_GDP_STRUCT.unpack_from(buffer, offset))

    @classmethod
    def unpack(cls, buffer):
        return cls.from_tuple(_GDP_STRUCT.unpack(buffer))

    def pack(self):
        return _GDP_STRUCT.pack(*dataclasses.astuple(self))
    
    def pack_into(self, buffer, offset: int):
        return _GDP_STRUCT.pack_into(buffer, offset, *dataclasses.astuple(self))

    def calculate_header_crc(self):
        self.flags |= HeaderFlag.CRC_HEADER
        self.header_crc = binascii.crc_hqx(self.pack()[:58], _CRC_INITIAL)

    def for_payload(self, payload: bytes):
        #self.flags |= HeaderFlag.CRC_HEADER | HeaderFlag.CRC_PAYLOAD
        self.length = len(payload)
        #self.header_crc = binascii.crc_hqx(self.pack()[:58], _CRC_INITIAL)
        #self.payload_crc = binascii.crc_hqx(payload, _CRC_INITIAL)


def make_event_caps(caps: Optional[bytes] = None, typ: PayloadType = PayloadType.CAPS):
    hdr = GdpHeader(
        version_major=1,
        version_minor=0,
        flags=0, # HeaderFlag.CRC_PAYLOAD | HeaderFlag.CRC_HEADER,
        typ=typ,
        length=0,
        pts=0,
        duration=0,
        offset=0,
        offset_end=0,
        buffer_flags=0,
        dts=0,
        header_crc=0,
        payload_crc=0,
    )

    if caps is None:
        return hdr.pack()
    
    caps += b'\0'
    hdr.for_payload(caps)
    return hdr.pack() + caps


async def gdp_client():
    print('Starting gdp_client: localhost:3000')
    reader, writer = await asyncio.open_connection('::1', 3000)
    start_pts = time.monotonic_ns()

    print('Sending caps')
    writer.write(make_event_caps(
        b'GstEventStreamStart, stream-id=(string)7eb0bc65a00cb7f0e0f4911d84b87e98ccc30096e59f5647f99f25e5fc5e2f96/src, flags=(GstStreamFlags)GST_STREAM_FLAG_NONE;',
        typ=PayloadType.EVENT_STREAM_START))
    writer.write(make_event_caps(b'text/x-raw'))
    writer.write(make_event_caps(
        b'GstEventSegment, segment=(GstSegment)"segment, flags=(GstSegmentFlags)GST_SEGMENT_FLAG_NONE, rate=(double)1, applied-rate=(double)1, format=(GstFormat)time, base=(guint64)0, offset=(guint64)0, start=(guint64)0, stop=(guint64)18446744073709551615, time=(guint64)0, position=(guint64)0, duration=(guint64)18446744073709551615;";',
        typ=PayloadType.EVENT_SEGMENT))
    await writer.drain()


    # base packet, to avoid re-alloc
    pkt = GdpHeader(
        version_major=1,
        version_minor=0,
        flags=0, # HeaderFlag.CRC_PAYLOAD | HeaderFlag.CRC_HEADER,
        typ=PayloadType.BUFFER,
        length=0,
        pts=0,
        duration=400_000,
        offset=0xffffffffffffffff,
        offset_end=0xffffffffffffffff,
        buffer_flags=0,
        dts=0,
        header_crc=0,
        payload_crc=0,
    )

    while 1:
        pkt.dts = pkt.pts = time.monotonic_ns() - start_pts
        print(f'packet {pkt.dts}')
        payload = f'Hello {pkt.dts}\n'.encode('utf-8')
        pkt.for_payload(payload)

        o = pkt.pack() + payload
        print(binascii.hexlify(o))
        writer.write(o)
        await writer.drain()
        await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(gdp_client())
