#!/usr/bin/env python3
#

import re
from .serialio import SerialIO


class Hdmi2Usb(SerialIO):

    PROMPT = b'HDMI2USB>'
    DEBUGVAL = 'HDMI Input {} debug on'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def enable_debug(self, indev =None):
        if self.port is None or not self.port.isOpen():
            self.open()
        for indev in range(2):
            self.timed_send(b'\r\n')
            self.expect(Hdmi2Usb.PROMPT)
            debug_enable = str.encode('debug input' + str(indev) + '\r\n')
            self.timed_send(debug_enable)
            expecting = str.encode(Hdmi2Usb.DEBUGVAL.format(indev))
            if not self.expect(expecting, multiline=True, timeout=2):
                self.timed_send(debug_enable)

    def sampler(self, callback, indev =None):
        self.enable_debug(indev)
        samplre = re.compile(r'^dvisampler(\d):.+// WER:\s*(\d+)\s+(\d+)\s+(\d+).+res:\s*(.*)$')
        while True:
            line = self.recv_line()
            strline = bytes.decode(line)
            result = samplre.match(strline)
            if result is not None:
                indev = int(result.group(1))
                err0 = int(result.group(2))
                err1 = int(result.group(3))
                err2 = int(result.group(4))
                res = result.group(5)
                callback(indev, err0 | err1 | err2, res)

    def watch(self, callback, indev =None):
        self.enable_debug(indev)
        while True:
            line = self.recv_line()
            callback(line)

