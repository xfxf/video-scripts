#!/usr/bin/env python3
"""
streamtext_client.py - A client to scrape the StreamText.Net live feed.
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

from dataclasses import dataclass, field
import requests
from time import sleep
from typing import Iterator, List, Optional
from urllib.parse import unquote

_TEXT_DATA_URL = 'https://www.streamtext.net/text-data.ashx'


@dataclass
class TextData:
    # Basic mode: plain text. New line is \r\n. Backspace is \x08.
    basic: Optional[str] = None

    # TODO: Implement other message types
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
    """A single response from a StreamText.net live stream."""
    first_position: int
    last_position: int
    events: List[TextData] = field(default_factory=list)

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

    def _get(self, event: str, last: int,
             language: Optional[str]) -> Optional[TextDataResponse]:
        """
        Gets a single event from the StreamText service.

        Returns:
            A single TextDataResponse, or None if no event is available.
        """
        r = self._session.get(_TEXT_DATA_URL,
                              params={
                                  'event': event,
                                  'last': str(last),
                                  'language': language,
                              })

        if r.status_code == 200:
            return TextDataResponse.from_json(r.json(), last)

        if r.status_code == 404:
            # Stream offline, reset position
            return TextDataResponse(first_position=last, last_position=-1)

        if r.status_code in (502, 503, 504):
            # Server issue
            return

        raise Exception(f'Unexpected HTTP {r.status_code}: {r.url}')

    def stream(
        self,
        event: str,
        last: int = -1,
        language: Optional[str] = None,
    ) -> Iterator[Optional[TextDataResponse]]:
        """
        Streams events from StreamText as an iterator.

        The stream continues until the event ends.
        
        Args:
            event: StreamText.net event identifier.
            last: Position to start from. Defaults to -1 (jump to real-time).
            language: Language code to stream text in. Required only for
                multi-lingual streams.
        
        Yields:
            TextDataResponse of the server's response.
            In the event of server errors, this yields None, and the stream
            may be resumed.
        
        Returns:
            None at the end of the stream.
        """
        while True:
            r = self._get(event, last, language)
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
    """Rubs-out any backspace characters in the terminal."""
    return d.replace('\x08', '\x08 \x08')


def main():
    from argparse import ArgumentParser
    import sys

    parser = ArgumentParser(
        description='Show a live feed from StreamText.net.',
        epilog=("StreamText's demo stream can be viewed with: "
                '%(prog)s IHaveADream -l en'),
    )
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
    options = parser.parse_args()

    client = StreamTextClient()
    stream = client.stream(options.event[0], options.last, options.language)
    print(f'Streaming {options.event[0]} from {options.last} in '
          f'{options.language or "unknown language"}...')

    for msg in stream:
        for e in msg.events:
            if e.basic:
                sys.stdout.write(_handle_bs(e.basic))

        sys.stdout.flush()
        sleep(1)

    print('Stream ended.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
