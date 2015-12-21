#!/usr/bin/python
import serial
import Tkinter

SERIAL = "/dev/ttyVIZ0"
EXPECT = "HDMI2USB>"
INIT = """
video_mode 10
output0 on
output1 off
encoder on
encoder quality 85
"""

CAMERA = """
video_matrix connect input0 output0
video_matrix connect input0 encoder
"""

SLIDES = """
video_matrix connect input1 output0
video_matrix connect input1 encoder
"""

def initHDMI2USB():
    try:
	ser = serial.Serial(SERIAL, 115200, timeout=3, rtscts = False, dsrdtr = False)
    	print "Initialising %s" % (SERIAL)
    	ser.write(INIT)
    	return ser
    except serial.SerialException:
	print "Could not open %s" % (SERIAL)
	return None

def keyHandler(event):
    if (event.char == 'q'):
        root.quit()
    elif event.char == '1':
        print CAMERA
        ser.write(CAMERA)
    elif event.char == '2':
        print SLIDES
        ser.write(SLIDES)
    #while True:
    #    try:
    #        print repr(ser.readline())
    #    except serial.serialutil.SerialException, e:
    #        print e
    #        break

ser = initHDMI2USB()

root = Tkinter.Tk()
root.geometry('400x200+100+100')
root.wm_title("HDMI2USB Serial Control")

label = Tkinter.Label(root, width=400, height=300, text='Press 1 for camera, 2 for slides, or q to quit')
label.pack(fill=Tkinter.BOTH, expand=1)
label.bind('<Key>', keyHandler)
label.focus_set()
 
root.mainloop()

print "Closing serial port"
ser.close()

