"""
tstext_to_cea608gdp - convert timestampped text to cea608json over gdp
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

File format: `timestamp_in_millis: text`, eg:

```
1000: hello
1300: world
```

"""

import argparse
import asyncio
import json

import gdp



async def push_tstext(fn, framerate: int = 30, mode: str = 'RollUp3', host: str = '::1', port: int = 3000):
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
        pts=0,
        # tttojson needs a duration, even for non-PopOn captions.
        duration=1_000_000_000 // framerate,
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

    print(f'Reading captions from {fn}...')
    with open(fn, 'r') as f:
        for l in f:
            ts, d = l.split(':')
            pkt.dts = pkt.pts = int(ts) * 1_000_000  # ms -> ns
            d = d.strip()
            # setting a duration means tttocea608 will smear
            pkt.duration = int((1_000_000_000 / framerate) * len(d))
            od = json.dumps(dict(
                lines=[dict(
                    chunks=[dict(
                        text=d,
                        style='White',
                        underline=False,
                    )],
                    carriage_return=False,
                )],
                mode=mode,
            ))

            payload = od.encode('utf-8')
            pkt.for_payload(payload)
            writer.write(pkt.pack() + payload)
            await writer.drain()

    print('All done.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_fn', nargs=1)
    parser.add_argument('--framerate', type=int, default=30)
    parser.add_argument('--mode', default='RollUp3')
    parser.add_argument('--host', default='::1')
    parser.add_argument('--port', type=int, default=3000)

    options = parser.parse_args()
    asyncio.run(push_tstext(
        fn=options.input_fn[0],
        framerate=int(options.framerate),
        mode=options.mode,
        host=options.host,
        port=int(options.port),
    ))


if __name__ == '__main__':
    main()
