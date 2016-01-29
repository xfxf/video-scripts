#!/usr/bin/env python3

import queue
import threading
import tkinter
import argparse
from enum import Enum

from opsis.hdmi2usb import *


class SerialThread(threading.Thread):

    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.hdmi2usb = Hdmi2Usb(**kwargs)

    def set_callback(self, callback):
        self.callback = callback

    def run(self):
        self.hdmi2usb.sampler(self.callback)


class Hdmi2UsbStatus(Enum):
    UNKNOWN = 0
    GOOD = 1
    ERRORS = 2


class App:
    """
    This is a simple tkinter anpplication to monitor status of an opsis hdmi2usb
    """
    TIMEOUT = 2.0

    def __init__(self, **kwargs):
        self.timeout = App.TIMEOUT
        self.events = queue.Queue()
        self.root = tkinter.Tk()
        self.root.geometry('+100+100')
        self.root.wm_title('HDMI2USB Status')
        self.images = [
            tkinter.PhotoImage(file='off.gif'),
            tkinter.PhotoImage(file='ok.gif'),
            tkinter.PhotoImage(file='error.gif'),
        ]
        self.textlabel = tkinter.Label(self.root, text='HDMI2USB Status:', justify=tkinter.LEFT)
        self.textlabel.pack()
        self.imagelabel = [None, None]
        self.status = [None, None]
        for i in range(2):
            self.imagelabel[i] = tkinter.Label(self.root, image=self.images[0], justify=tkinter.RIGHT)
            self.imagelabel[i].pack()
            self.status[i] = { 'time': time.time(), 'status': Hdmi2UsbStatus.UNKNOWN, 'res': None }
        self.monitor = SerialThread(**kwargs)

    def schedule(self):
        self.root.after(1000, self.check_status)

    def run(self):
        self.monitor.set_callback(self.set_status)
        self.monitor.start()
        self.schedule()
        self.root.mainloop()

    @property
    def _now(self):
        return time.time()

    def set_status(self, indev, errs, res):
        # Note that UNKNOWN is set elsewhere when this event time becomes outdated
        status = Hdmi2UsbStatus.GOOD if errs == 0 else Hdmi2UsbStatus.ERRORS
        event = {'indev': indev, 'time': self._now, 'status': status, 'res': res}
        self.events.put(event)

    def check_status(self):
        status = copy.deepcopy(self.status)
        if not self.events.empty():
            while not self.events.empty():
                event = self.events.get()
                status[event['indev']] = event
        for indev in range(2):
            if status[indev]['status'] != Hdmi2UsbStatus.UNKNOWN and status[indev]['time'] + self.timeout < self._now:
                status['time'] = time._now
                status['status'] = Hdmi2UsbStatus.UNKNOWN
            if self.status[indev]['status'] != status[indev]['status']:
                """ need to update the UI """
                newimage = self.images[status[indev]['status'].value]
                self.imagelabel[indev].configure(image=newimage)
                self.imagelabel[indev].pack()
            self.status[indev] = status[indev]
        self.schedule()


def get_args():
    parser = argparse.ArgumentParser(description='Monitor Opsis debug output')
    parser.add_argument('--port', default=Hdmi2Usb.PORT_DEFAULTS['port'], required=False, help="serial port" )
    parser.add_argument('--speed', default=Hdmi2Usb.PORT_DEFAULTS['baudrate'], required=False, help="serial baud rate")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    app = App(port = args.port, baudrate = args.speed)

    app.run()


if __name__ == '__main__':
    main()

