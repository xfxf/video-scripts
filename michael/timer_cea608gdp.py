"""
timer_cea608gdp - insert simple pts counter for cea608json over gdp
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

import gdp

_COLOURS = ['White', 'Green', 'Blue', 'Cyan', 'Red', 'Yellow', 'Magenta']


async def push_pts_timer(framerate: int = 30,
                         mode: str = 'PopOn',
                         host: str = '::1',
                         port: int = 3000,
                         length: int = 0):
    print(f'Connecting to {host} port {port}')
    reader, writer = await asyncio.open_connection(host, port)

    gdp.gdp_setup(writer, json_fmt=True)
    await writer.drain()

    pkt = gdp.GdpHeader(
        version_major=1,
        version_minor=0,
        flags=gdp.HeaderFlag.CRC_HEADER,
        typ=gdp.PayloadType.BUFFER,
        length=0,
        # Put the first clear command on the second frame
        pts=(2_000_000_000 // framerate),
        duration=(1_000_000_000 // framerate),
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

    # Start at 00m01s00f
    pts_sec = 1
    # Stay on screen for 1 frame less than 1 second.
    pkt.duration = 1_000_000_000 # - (1_000_000_000 // framerate)
    while length == 0 or pts_sec < length:
        pkt.pts = pts_sec * 1_000_000_000  # seconds -> ns
        pkt.dts = pkt.pts - 1_000_000_000
        colour = _COLOURS[pts_sec % len(_COLOURS)]
        payload = json.dumps(dict(
            mode=mode,
            lines=[
                dict(
                    chunks=[dict(
                        text=f'{pts_sec:02d}: {colour}!',
                        style=colour,
                        underline=False,
                    )],
                ),
            ],
            clear=False,
        )).encode('utf-8')
        pkt.for_payload(payload)
        writer.write(pkt.pack() + payload)
        await writer.drain()
        pts_sec += 1

    print('All done.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--framerate', type=int, default=30)
    parser.add_argument('--mode', default='PopOn')
    parser.add_argument('--host', default='::1')
    parser.add_argument('--port', type=int, default=3000)
    parser.add_argument('--length',
                        type=int,
                        default=0,
                        help='Number of seconds to run, or 0 to run forever')

    options = parser.parse_args()
    asyncio.run(
        push_pts_timer(
            framerate=int(options.framerate),
            mode=options.mode,
            host=options.host,
            port=int(options.port),
            length=int(options.length),
        ))


if __name__ == '__main__':
    main()
