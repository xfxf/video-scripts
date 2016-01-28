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
		pipeline = """
            dv1394src !\
            multiqueue !\
		dvdemux name=demux \
                alsasrc device=%s provide-clock=false !\
                audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !\
                queue !\
                mux. \
            demux. !\
                dvdec !\
                deinterlace !\
                videoconvert !\
                videorate !\
                videoscale !\
                video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !\
                queue !\
                mux. \
            matroskamux name=mux !\
        	tcpclientsink port=1000%s host=%s
			   """ % ('hw:1,0', '0', '192.168.0.70')

		clock = Gst.SystemClock.obtain()
		self.clock = GstNet.NetClientClock.new('voctocore', '192.168.0.70', 9998, clock.get_time())
		print('obtained NetClientClock from host', self.clock)

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
