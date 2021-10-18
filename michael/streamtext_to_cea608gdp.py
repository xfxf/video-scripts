"""
streamtext_to_cea608gdp - convert streamtext input to cea608json over gdp
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

"""

import argparse
import asyncio
import json
import time
from typing import Optional

import gdp
from streamtext_client import StreamTextClient



async def push_tstext(event: str, language: Optional[str] = None, last: int = -1, framerate: int = 30, mode: str = 'RollUp3', host: str = '::1', port: int = 3000):
    print(f'Connecting to {host} port {port}')
    reader, writer = await asyncio.open_connection(host, port)

    gdp.gdp_setup(writer, json_fmt=True)
    await writer.drain()

    client = StreamTextClient()
    stream = client.stream(event, last=last, language=language)

    pkt = gdp.GdpHeader(
        version_major=1,
        version_minor=0,
        flags=gdp.HeaderFlag.CRC_HEADER,
        typ=gdp.PayloadType.BUFFER,
        length=0,
        pts=0,
        # tttojson needs a duration, even for non-PopOn captions.
        # Lets make it 2 frames.
        duration=2_000_000_000 // framerate,
        offset=0xffffffffffffffff,
        offset_end=0xffffffffffffffff,
        buffer_flags=0,
        dts=0,
        header_crc=0,
        payload_crc=0,
    )

    # Clear the screen first
    payload = json.dumps(dict(
        mode=mode,
        lines=[],
        clear=True,
    )).encode('utf-8')
    pkt.for_payload(payload)
    writer.write(pkt.pack() + payload)
    await writer.drain()

    print(f'Streaming captions from {event}...')
    start_pts = time.monotonic_ns()
    d = ''
    for msg in stream:
        pkt.dts = pkt.pts = time.monotonic_ns() - start_pts
        # TODO: handle text edits
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
                mode=mode,
            ))
            print('>>', od)
            payload = od.encode('utf-8')
            pkt.for_payload(payload)
            writer.write(pkt.pack() + payload)
            await writer.drain()
        
        await asyncio.sleep(.3)

    print('All done.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('event',
                        nargs=1,
                        help='StreamText.net event ID to stream.')
    parser.add_argument(
        '--last',
        default=-1,
        type=int,
        help=('First event ID to read from. When -1 (the default), '
              'automatically catch up to live.'),
    )
    parser.add_argument(
        '-l',
        '--language',
        help=('Subtitle language code to stream. Required for multi-lingual '
              'streams.'),
    )
    parser.add_argument('--framerate', type=int, default=30)
    parser.add_argument('--mode', default='RollUp3')
    parser.add_argument('--host', default='::1')
    parser.add_argument('--port', type=int, default=3000)

    options = parser.parse_args()
    asyncio.run(push_tstext(
        event=options.event[0],
        last=int(options.last),
        language=options.language,
        framerate=int(options.framerate),
        mode=options.mode,
        host=options.host,
        port=int(options.port),
    ))


if __name__ == '__main__':
    main()
