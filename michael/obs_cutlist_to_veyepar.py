#!/usr/bin/env python3
"""
obs_cutlist_to_veyepar.py - converts a cutlist.lua cut list to Veyepar format
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

------

cutlist.lua format:

* newline separated JSON file (may have DOS linefeeds)
* each object is:
  * ts: ISO 8601 date
  * event: event type: "LOAD", "SCENE", "CUT", "CLOSE"
  * data: optional data (scene name)


Veyepar cut list format defined in:

https://github.com/CarlFK/voctomix-outcasts/blob/master/generate-cut-list.py

* text file with events split by newline (always UNIX linefeeds)
* each line has a timestamp: strftime("%Y-%m-%d/%H_%M_%S")

"""

import argparse
from datetime import datetime
import json


ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'
VEYEPAR_FORMAT = '%Y-%m-%d/%H_%M_%S\n'


def read_obs_cutlist(fh):
    last_ts = None
    for line in fh:
        event = json.loads(line)
        if event['event'] not in ('SCENE', 'CUT'):
            # Only pass SCENE and CUT events
            continue

        event['ts'] = datetime.strptime(event['ts'], ISO_FORMAT)

        if last_ts is not None and last_ts == event['ts']:
            # Only emit one event in a second
            continue
        last_ts = event['ts']

        yield event


def write_veyepar_cutlist(fh, events):
    for event in events:
        fh.write(event['ts'].strftime(VEYEPAR_FORMAT).encode('utf-8'))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input_cutlist',
        type=argparse.FileType('r'),
        help='Input OBS cutlist file (newline separated JSON)',
        nargs=1,
    )

    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('wb'),
        help='Output Veyepar cutlist file',
        required=True,
    )

    options = parser.parse_args()
    write_veyepar_cutlist(options.output, read_obs_cutlist(options.input_cutlist[0]))


if __name__ == '__main__':
    main()
