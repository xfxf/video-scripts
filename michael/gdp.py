"""
gdp.py - gstreamer data protocol
Copyright 2021 Michael Farrell <micolous+git@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This script runs `IHaveADream` from streamtext.net, using streamtext_client.

gstgit-launch -v \
  cccombiner name=ccc ! timecodestamper ! cea608overlay ! \
    timeoverlay time-mode=time-code ! x264enc pass=quant ! \
    mp4mux name=muxer filesink location=/tmp/608live.mp4 \
  videotestsrc num-buffers=600 pattern=ball ! video/x-raw,width=1280,height=720 ! queue ! ccc. \
  tcpserversrc port=3000 ! gdpdepay ! queue ! tttocea608 ! \
    closedcaption/x-cea-608,framerate=30/1 ! queue ! ccconverter ! \
    closedcaption/x-cea-708,format=cc_data ! ccc.caption
"""

import asyncio
import binascii
import dataclasses
from enum import IntFlag, IntEnum
import json
from struct import Struct
import time
from typing import Optional
import uuid

from streamtext_client import StreamTextClient

# https://github.com/GStreamer/gst-plugins-bad/blob/master/gst/gdp/dataprotocol.c
# https://github.com/GStreamer/gst-plugins-bad/blob/master/gst/gdp/dataprotocol.h
# https://github.com/GStreamer/gstreamer/blob/master/docs/images/gdp-header.png
# fields are big endian

_GST_MINI_OBJECT_FLAG_LAST = 1 << 4
_GST_EVENT_NUM_SHIFT = 8
_CRC_INITIAL = 0xffff

def gst_crc16(data: bytes) -> int:
    """gst_dp_crc is the same as crc_hqx, but with all output bits flipped."""
    return binascii.crc_hqx(data, _CRC_INITIAL) ^ 0xffff


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
        self.header_crc = gst_crc16(self.pack()[:58])

    def for_payload(self, payload: bytes):
        if self.flags & HeaderFlag.CRC_PAYLOAD > 0:
            self.payload_crc = gst_crc16(payload)
        else:
            self.payload_crc = 0

        self.length = len(payload)
        if self.flags & HeaderFlag.CRC_HEADER > 0:
            self.header_crc = gst_crc16(self.pack()[:58])
        else:
            self.header_crc = 0


def make_event_caps(caps: Optional[bytes] = None, typ: PayloadType = PayloadType.CAPS):
    hdr = GdpHeader(
        version_major=1,
        version_minor=0,
        flags=HeaderFlag.CRC_PAYLOAD | HeaderFlag.CRC_HEADER,
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
    stream_id = uuid.uuid4().hex

    print('Sending caps')
    writer.write(make_event_caps(
        f'GstEventStreamStart, stream-id=(string){stream_id}/src, flags=(GstStreamFlags)GST_STREAM_FLAG_SPARSE;'.encode('utf-8'),
        typ=PayloadType.EVENT_STREAM_START))
    #writer.write(make_event_caps(b'text/x-raw'))
    writer.write(make_event_caps(b'application/x-json,format=cea608'))
    writer.write(make_event_caps(
        b'GstEventSegment, segment=(GstSegment)"segment, flags=(GstSegmentFlags)GST_SEGMENT_FLAG_NONE, rate=(double)1, applied-rate=(double)1, format=(GstFormat)time, base=(guint64)0, offset=(guint64)0, start=(guint64)0, stop=(guint64)18446744073709551615, time=(guint64)0, position=(guint64)0, duration=(guint64)18446744073709551615;";',
        typ=PayloadType.EVENT_SEGMENT))
    await writer.drain()

    # base packet, to avoid re-alloc
    pkt = GdpHeader(
        version_major=1,
        version_minor=0,
        flags=HeaderFlag.CRC_HEADER,
        typ=PayloadType.BUFFER,
        length=0,
        pts=0,
        # tttojson needs a duration, even for non-PopOn captions.
        duration=1, #400_000,
        offset=0xffffffffffffffff,
        offset_end=0xffffffffffffffff,
        buffer_flags=0,
        dts=0xffffffffffffffff,
        header_crc=0,
        payload_crc=0,
    )
    streamtext = StreamTextClient()
    stream = streamtext.stream('IHaveADream', language='en')
    d = ''

    #while 1:
    for msg in stream:
        pkt.pts = time.monotonic_ns() - start_pts
        for evt in msg.events:
            if evt.basic:
                d += evt.basic

        if ' ' in d:
            # We want to only output on a word boundary.
            s = d.rindex(' ')
            od = d[:s]
            d = d[s + 1:]

            od = json.dumps(dict(
                lines=[dict(
                    chunks=[dict(
                        text=od,
                        style='White',
                        underline=False,
                    )],
                    carriage_return=False,
                )],
                mode='RollUp3',
            ))

            print('>>>', od)
            payload = od.encode('utf-8')

            #print(f'packet {pkt.dts}')
            #payload = f'Hello {pkt.dts}\n'.encode('utf-8')
            pkt.for_payload(payload)

            o = pkt.pack() + payload
            #print(binascii.hexlify(o))
            writer.write(o)
            await writer.drain()

        await asyncio.sleep(.3)


if __name__ == '__main__':
    asyncio.run(gdp_client())
