#!/usr/bin/env python3
"""
PIPELINES:
 * dvpulse
 * hdmi2usb
 * test

Intended uses (NOTE expected environment variables):
 * lca-videomix-ingest.py dvpulse 0
 * lca-videomix-ingest.py hdmi2usb 1
""" 

import sys
import gi
import signal
import os
import socket

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstNet, GObject

# init GObject & Co. before importing local classes
GObject.threads_init()
Gst.init([])

class Source(object):
    def __init__(self, pipeline_name, pulse_device, voc_port, voc_core_hostname, hdmi2usb_device):

        voc_core_ip = socket.gethostbyname(voc_core_hostname)
        print(pipeline_name, voc_core_ip, voc_port)

        if pipeline_name == 'dvpulse':
            pipeline = """
            dv1394src !
            multiqueue !
            dvdemux !
                dvdec !
                deinterlace !
                videoconvert !
                videorate !
                videoscale !
                video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !
                queue !
            mux. 
                pulsesrc device=%s !
                audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !
                queue !
            mux.
                matroskamux name=mux !
                    tcpclientsink port=1000%s host=%s
                """ % (pulse_device, voc_port, voc_core_ip)
           
        elif pipeline_name == 'blackmagic':
            pipeline = """
            decklinkvideosrc !
                queue !
                videoconvert !
                videorate !
                videoscale !
                video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !
                queue !
                mux. 
            decklinkaudiosrc !
                audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !
                queue !
                mux. 
            matroskamux name=mux !\
                tcpclientsink port=1000%s host=%s
                """ % (voc_port, voc_core_ip)
 
        elif pipeline_name == 'hdmi2usb':
            pipeline = """
            v4l2src device=%s !
                image/jpeg,width=1280,height=720 !
                jpegdec !
                videoconvert !
                tee name=t ! queue ! 
                    videoconvert ! fpsdisplaysink sync=false t. ! 
                videorate !
                video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !
                queue !
                mux. 
            audiotestsrc !
                audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !
                queue !
                mux. 
            matroskamux name=mux !\
                tcpclientsink port=1000%s host=%s
                """ % (hdmi2usb_device, voc_port, voc_core_ip)

        else:
            pipeline = """
        videotestsrc pattern=ball foreground-color=0x00ff0000 background-color=0x00440000 !
                 timeoverlay !
                 video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !
                 mux.

         audiotestsrc freq=330 !
                 audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !
                 mux.

         matroskamux name=mux !
                 tcpclientsink port=1000%s host=%s
                 """ % (voc_port, voc_core_ip)

        print(pipeline)

        self.clock = GstNet.NetClientClock.new('voctocore', voc_core_ip, 9998, 0)
        print('obtained NetClientClock from host', self.clock)

        print('waiting for NetClientClock to sync…')
        self.clock.wait_for_sync(Gst.CLOCK_TIME_NONE)

        print('starting pipeline')
        self.senderPipeline = Gst.parse_launch(pipeline)
        self.senderPipeline.use_clock(self.clock)
        self.src = self.senderPipeline.get_by_name('src')

        # Binding End-of-Stream-Signal on Source-Pipeline
        self.senderPipeline.bus.add_signal_watch()
        self.senderPipeline.bus.connect("message::eos", self.on_eos)
        self.senderPipeline.bus.connect("message::error", self.on_error)

        print("playing")
        self.senderPipeline.set_state(Gst.State.PLAYING)


    def on_eos(self, bus, message):
        print('Received EOS-Signal')
        sys.exit(1)

    def on_error(self, bus, message):
        print('Received Error-Signal')
        (error, debug) = message.parse_error()
        print('Error-Details: #%u: %s' % (error.code, debug))
        sys.exit(1)

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
  
    # populate machine-specific things
    voc_core_hostname = os.environ.get('VOC_CORE', 'localhost')
    hdmi2usb_device = os.environ.get('HDMI2USB', '/dev/video0')
    pulse_device = os.environ.get('PULSE', 'alsa_input.usb-Burr-Brown_from_TI_USB_Audio_CODEC-00.analog-stereo')

    # get parameters (pipeline_name, vocto port ending digit in 1000x)
    try:
        voc_pipeline = sys.argv[1]
        voc_port = sys.argv[2]
    except (NameError, IndexError):
        print("Requires parameters: pipeline_name, vocto_port_ending_digit")
        sys.exit()
    
    src = Source(pipeline_name=voc_pipeline,
                 pulse_device=pulse_device,
                 voc_port=voc_port,
                 voc_core_hostname=voc_core_hostname,
                 hdmi2usb_device=hdmi2usb_device)
    
    mainloop = GObject.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        print('Terminated via Ctrl-C')


if __name__ == '__main__':
    main()
