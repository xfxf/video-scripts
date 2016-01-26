#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import sys, gi, signal
import threading
import time
from pprint import pprint

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

GObject.threads_init()
Gst.init([])

def on_error(bus, message):
    (error, debug) = message.parse_error()
    print('Error-Details: #%u: %s' % (error.code, debug))
    sys.exit(1)

p = """
	hdv1394src ! decodebin ! videoconvert ! fpsdisplaysink sync=false
"""

pipe = Gst.parse_launch(p)
pipe.bus.add_signal_watch()
pipe.bus.connect("message::error", on_error)
pipe.set_state(Gst.State.PLAYING)

mainloop = GObject.MainLoop()
signal.signal(signal.SIGINT, signal.SIG_DFL)

def showpipeline():
 # FIXME: show constructed pipeline (dynamic pad resolution)
 while True:
  time.sleep(2)
  print(p)

threading.Thread(target=showpipeline).start()

mainloop.run()

