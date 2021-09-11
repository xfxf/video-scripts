#!/usr/bin/env python
"""
streamtext_monitor.py - Export StreamText.Net metrics to Prometheus.
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

import asyncio
from argparse import ArgumentParser
from typing import List
from prometheus_client import start_http_server, Gauge

from streamtext_client import StreamTextClient

_CLIENT = StreamTextClient()
_LAST_RESET = Gauge(
    'streamtext_last_reset_ts',
    'UNIX time of when the stream last reset. A stream will (repeatedly!) '
    'reset when the stenographer pauses or stops their session.',
    ['event'])
_LAST_TEXT = Gauge(
    'streamtext_last_text_ts',
    'UNIX time of when the last new text was written by the stenographer.',
    ['event'])
_LAST_SEEN = Gauge(
    'streamtext_last_seen_ts',
    'UNIX time of when StreamText.net last returned a response to polling.',
    ['event'])
_LAST_POSITION = Gauge(
    'streamtext_last_position',
    'Last message ID from StreamText.net. This resets if the session is paused or restarted.',
    ['event'])


class StreamMonitor:
    def __init__(self, event: str):
        self._event = event
        _LAST_TEXT.labels(event).set(0)
        _LAST_SEEN.labels(event).set(0)
        self.reset()

    def reset(self):
        self._stream = _CLIENT.stream(self._event)
        _LAST_POSITION.labels(self._event).set(-1)
        _LAST_RESET.labels(self._event).set_to_current_time()

    async def loop(self):
        try:
            r = next(self._stream)
        except StopIteration:
            self.reset()
            # Wait a little longer...
            await asyncio.sleep(5)
            return asyncio.create_task(self.loop())

        if r:
            self._last_msg = r
            _LAST_SEEN.labels(self._event).set_to_current_time()
            _LAST_POSITION.labels(self._event).set(
                self._last_msg.last_position)

            if r.events:
                _LAST_TEXT.labels(self._event).set_to_current_time()

        await asyncio.sleep(1)
        return asyncio.create_task(self.loop())


async def main_async(events: List[str]):
    for e in events:
        m = StreamMonitor(e)
        asyncio.create_task(m.loop())

    while True:
        await asyncio.sleep(1)


def main():
    parser = ArgumentParser(
        prog='streamtext_monitor',
        description=('Exports metrics relating to a StreamText.net feed in a '
                     'Prometheus-compatible format.'),
    )
    parser.add_argument('events',
                        nargs='+',
                        help='A list of StreamText.net event IDs to monitor')
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for Prometheus metrics exporter to listen on (HTTP)')

    options = parser.parse_args()

    print(f'streamtext_monitor: port={options.port}, events={options.events}')
    start_http_server(options.port)
    asyncio.run(main_async(options.events))


if __name__ == '__main__':
    main()
