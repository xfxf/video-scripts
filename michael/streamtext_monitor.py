#!/usr/bin/env python
"""
streamtext_monitor.py - Export StreamText.Net metrics.
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
from datetime import datetime, timezone
import json
from time import sleep, time
from typing import Optional

from streamtext_client import StreamTextClient, TextDataResponse


_CLIENT = StreamTextClient()


def _now() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)


class StreamMonitor:
    def __init__(self, event: str):
        self._event = event
        self.run = True
        self.last_seen = None  # type: Optional[datetime]
        self._last_msg = None  # type: Optional[TextDataResponse]
        self.reset()

    def reset(self):
        self.buffer = ''
        self._stream = _CLIENT.stream(self._event)
        self.last_reset = _now()  # type: datetime

    @property
    def last_position(self) -> int:
        return self._last_msg.last_position if self._last_msg else -1

    async def loop(self):
        # Poll a response from the stream
        try:
            r = next(self._stream)
        except StopIteration:
            self.reset()
            # Wait a little longer...
            await asyncio.sleep(5)
            return asyncio.create_task(self.loop())

        if r:
            self._last_msg = r
            self.last_seen = _now()

            for e in r.events:
                if not e.basic:
                    # TODO: handle other events
                    continue

                for char in e.basic:
                    if char == '\x08':
                        # Backspace
                        self.buffer = self.buffer[:-1]
                    else:
                        self.buffer += char
                
                # Memory limit, take the last 512 bytes
                self.buffer = self.buffer[-512:]

        await asyncio.sleep(1)
        return asyncio.create_task(self.loop())

    def dump_state(self):
        return json.dumps(dict(
            event=self._event,
            now=_now().isoformat(),
            last_reset=self.last_reset.isoformat() if self.last_reset else None,
            last_seen=self.last_seen.isoformat() if self.last_seen else None,
            last_position=self.last_position,
            buffer=self.buffer,
        ))

async def main_async(events: list[str]):
    # Create all the monitors

    monitors = []
    for e in events:
        m = StreamMonitor(e)
        monitors.append(m)
        asyncio.create_task(m.loop())
    
    while True:
        for m in monitors:
            print(m.dump_state())
        await asyncio.sleep(1)


def main():
    parser = ArgumentParser()
    parser.add_argument('events', nargs='+')

    options = parser.parse_args()

    asyncio.run(main_async(options.events))


if __name__ == '__main__':
    main()
