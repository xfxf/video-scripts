#!/usr/bin/python3
import sys, gi, signal

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstNet, GObject

# init GObject & Co. before importing local classes
GObject.threads_init()
Gst.init([])

class Source(object):
	def __init__(self):
		# it works much better with a local file

		pipeline_videodv_audiopulse = """
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
                        tcpclientsink host=%s port=10000
                """ % ('alsa_input.usb-Burr-Brown_from_TI_USB_Audio_CODEC-00.analog-stereo', '192.168.0.10')

		pipeline_hdmi2usb_noaudio = """
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
                """ % ('/dev/video0', '1', '192.168.0.10')
		
		pipeline = pipeline_videodv_audiopulse

		self.clock = GstNet.NetClientClock.new('voctocore', '192.168.0.10', 9998, 0)
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

	src = Source()

	mainloop = GObject.MainLoop()
	try:
		mainloop.run()
	except KeyboardInterrupt:
		print('Terminated via Ctrl-C')


if __name__ == '__main__':
	main()
