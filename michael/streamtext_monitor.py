#!/usr/bin/env python3

# First:
# https://www.streamtext.net/text-data.ashx?event=EEEE&last=-1
#
# this gives:
#  HTTP 200 -> { lastPosition: 1208, i: [] }
# on error:
#  HTTP 404 -> then we try again

# then we do:
# https://www.streamtext.net/text-data.ashx?event=EEEE&last=1208
#
# this gives:
#  {"lastPosition":1210, "i":[{"format":"basic","d":"%20move"},{"format":"basic","d":"%20on%20from"}]}

# next we grab last=1210
#
# when no new data:
#   HTTP 200 => {"lastPosition":1210, "i":[]}
#   repeat request
# then on success:
#   HTTP 200 => {"lastPosition":1211, "i":[{"format":"basic","d":"%20"}]}

# last = 0
#   grabs everything!

from argparse import ArgumentParser
from dataclasses import dataclass, field
from datetime import datetime
import requests
import sys
from time import sleep
from typing import Iterator, Optional
from urllib.parse import unquote

_TEXT_DATA_URL = 'https://www.streamtext.net/text-data.ashx'


def _log(line: str):
    now = datetime.utcnow()
    print(f'{now.isoformat()}: {line}')


@dataclass
class TextData:
    basic: Optional[str] = None
    other: Optional[dict] = None

    @staticmethod
    def from_json(j) -> 'TextData':
        fmt = j.get('format')
        if fmt == 'basic':
            d = unquote(str(j.get('d', '')))
            return TextData(basic=d)
        else:
            return TextData(other=j)


@dataclass
class TextDataResponse:
    first_position: int
    last_position: int
    events: list[TextData] = field(default_factory=list)

    @staticmethod
    def from_json(j, first_position: int) -> 'TextDataResponse':
        try:
            last_position = int(j.get('lastPosition', 0))
        except:
            last_position = -1

        return TextDataResponse(
            first_position=first_position,
            last_position=last_position,
            events=[TextData.from_json(j) for j in j.get('i', [])],
        )


class StreamTextClient:
    def __init__(self):
        self._session = requests.Session()

    def _get(self, event: str, last: int) -> Optional[TextDataResponse]:
        """
        Gets a single event from the StreamText service.

        Returns:
            A single TextDataResponse, or None if no event is available.
        """
        r = self._session.get(_TEXT_DATA_URL, params=dict(
            event=event,
            last=str(last),
        ))

        if r.status_code == 200:
            return TextDataResponse.from_json(r.json(), last)
        
        if r.status_code == 404:
            # Stream offline, reset position
            return TextDataResponse(first_position=last, last_position=-1)
        
        if r.status_code in (502, 503, 504):
            # Server issue
            return

        raise Exception(f'Unexpected HTTP {r.status_code}: {r.url}')
    
    def stream(self, event: str, last: int = -1) -> Iterator[Optional[TextDataResponse]]:
        while True:
            r = self._get(event, last)
            if r is None:
                # Server issue, give empty response
                yield
            elif r.last_position == -1:
                # Stream offline, end the stream.
                return
            else:
                # Stream online, record last event ID.
                last = r.last_position
            
            yield r

def _handle_bs(d: str) -> str:
    return d.replace('\x08', '\x08 \x08')


def main():
    parser = ArgumentParser()
    parser.add_argument('event', nargs=1)
    parser.add_argument('--last', default=-1, type=int)
    options = parser.parse_args()

    client = StreamTextClient()
    stream = client.stream(options.event[0], options.last)

    for msg in stream:
        #_log(f'Events from {msg.first_position} to {msg.last_position}: {repr(msg)}')
        for e in msg.events:
            if e.basic:
                #_log(e)
                sys.stdout.write(_handle_bs(e.basic))

        sys.stdout.flush()
        
        # sleep a bit
        sleep(1)
    
    _log('Stream offline')


if __name__ == '__main__':
    main()
