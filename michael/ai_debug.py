#!/usr/bin/env python3
"""
ai_debug.py - Debugging timing from AI Media CaptionViewer
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
import datetime
import csv
import json
import sys
import textwrap

def get_requests_from_har(f):
    j = json.load(f)
    for entry in j['log']['entries']:
        url = entry['request']['url']
        if url.endswith('LiveSessionController.asmx/GetLiveSessionCaptionsUpdate') or url.endswith('LiveSessionController.asmx/DemoGetLiveSessionCaptionsUpdate'):
            # startedDateTime, requestJson, responseJson
            start_ts = datetime.datetime.fromisoformat(entry['startedDateTime'])
            request = json.loads(entry['request']['postData']['text'])
            response = json.loads(entry['response']['content']['text'])
            # FIXME: this doesn't implement all the message types, or text edits.
            yield start_ts, request, response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_har', nargs=1, type=argparse.FileType('r'))
    parser.add_argument('--show-empty', action='store_true')
    parser.add_argument('--csv', action='store_true')

    options = parser.parse_args()
    last_ts = None
    last_bytes_ts = None
    cf = None

    if options.csv:
        cf = csv.writer(sys.stdout)
        cf.writerow(['ts', 'seconds_since_last_request', 'seconds_since_last_text', 'chars', 'cps_since_last_text', 'cps_since_last_request'])

    for start_ts, req, resp in get_requests_from_har(options.input_har[0]):
        # Find the time since last request, in seconds; first is fake
        time_since_last = (start_ts - last_ts).total_seconds() if last_ts else 1.5
        last_ts = start_ts
        # demo uses oldEndPosition, live uses lastLiveOperationIndex
        req_last_index = req['lastLiveOperationIndex'] if 'lastLiveOperationIndex' in req else req['oldEndPosition']
        resp_ops = resp['d']['StreamingOperations']
        resp_op_count = len(resp_ops)
        text = ''.join(o['Text'] for o in resp_ops)
        resp_op_bytes = len(text)

        if not text:
            if options.show_empty:
                if cf:
                    cf.writerow([
                        start_ts.strftime('%H:%M:%S') + f'.{start_ts.microsecond // 1000:03d}',
                        f'{time_since_last:.1f}',
                        f'',
                        f'{resp_op_bytes}',
                        f'',
                        f'',
                    ])                    
                else:
                    print(f'{start_ts}, empty')
            continue


        # Find the time since last bytes
        if last_bytes_ts:
            time_since_bytes = (start_ts - last_bytes_ts).total_seconds()
        else:
            # First is fake!
            time_since_bytes = time_since_last
        last_bytes_ts = start_ts

        if cf:
            cf.writerow([
                start_ts.strftime('%H:%M:%S') + f'.{start_ts.microsecond // 1000:03d}',
                f'{time_since_last:.1f}',
                f'{time_since_bytes:.1f}',
                f'{resp_op_bytes}',
                f'{resp_op_bytes/time_since_bytes:.1f}',
                f'{resp_op_bytes/time_since_last:.1f}',
            ])
            continue
        print(f'{start_ts.strftime("%H:%M:%S")}: {time_since_bytes:.1f}s since last text, {resp_op_bytes} chars, {resp_op_bytes/time_since_bytes:.1f} CPS, {resp_op_bytes/time_since_last:.1f} CPS from last request {time_since_last:.1f}s ago')
        if text:
            print(textwrap.indent(text, '> ', lambda _: True))
            print()


if __name__ == '__main__':
    main()
