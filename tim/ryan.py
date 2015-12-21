#!/usr/bin/python
import time
import serial
import Tkinter

SERIAL = "/dev/ttyVIZ0"
EXPECT = "HDMI2USB>"
INIT = """
output0 on
output1 off
video_mode 10
encoder on
encoder quality 85
status
"""

CAMERA = """
video_matrix connect input0 output0
video_matrix connect input0 encoder
output1 off
status
"""

SLIDES = """
video_matrix connect input1 output0
video_matrix connect input1 encoder
output1 off
status
"""

def p(ser, dir, line):
    print "%i:%i %s %s" % (ser.inWaiting(), ser.outWaiting(), dir, line)

def getOutput(ser):
    failures = 0
    data = []
    while ser.inWaiting() > 0 or failures < 5:
        try:
            failures = 0
            data.append(ser.read())
        except serial.serialutil.SerialException, e:
            failures += 1
            time.sleep(0.1)
            break
    if data:
        for line in "".join(data).splitlines():
            p(ser, "-->", repr(line))

def write(ser, data):
    for line in data.splitlines():
        outdata = line+'\n'
        getOutput(ser)
        p(ser, "---", "")
        p(ser, "<--", repr(outdata))
        ser.write(outdata)
        getOutput(ser)
        ser.flush()
    getOutput(ser)

def initHDMI2USB():
    ser = serial.Serial(port=SERIAL, baudrate=115200, timeout=0, xonxoff=False, rtscts=False, dsrdtr=False)

    for i in range(1, 10):
        ser.flushInput()
        ser.flushOutput()

    if not ser.isOpen():
        print "Could not open %s" % (SERIAL)
        exit

    print "Initialising %s" % (SERIAL)
    write(ser, "\n")
    write(ser, INIT)
    return ser

def keyHandler(event):
    getOutput(ser)
    print "---"
    if (event.char == 'q'):
        root.quit()
    elif event.char == '1':
        write(ser, CAMERA)
    elif event.char == '2':
        write(ser, SLIDES)
    getOutput(ser)
    print "---"

ser = initHDMI2USB()

#make a TkInter Window
root = Tkinter.Tk()
root.geometry('400x200+100+100')
root.wm_title("HDMI2USB Serial Control")

# Create a label with instructions
label = Tkinter.Label(root, width=400, height=300, text='Press 1 for camera, 2 for slides, or q to quit')
label.pack(fill=Tkinter.BOTH, expand=1)
label.bind('<Key>', keyHandler)
label.focus_set()

root.mainloop()

print "Closing serial port"
ser.close()
