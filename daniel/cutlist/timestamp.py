#! /usr/bin/env python3

import termios, fcntl, sys, os, datetime, time
fd = sys.stdin.fileno()

tspath = ""

if (len(sys.argv) < 2):
    print("error: no file")
    exit(-1)
else:
    tspath = sys.argv[1]

def dumpTime():
    dt = datetime.datetime.now()
    timestring = dt.strftime('%Y-%m-%d/%H_%M_%S')
    print(timestring)
    with open(tspath, 'a') as f:
        f.write(timestring + "\n")

# The following is from: https://stackoverflow.com/questions/13207678/whats-the-simplest-way-of-detecting-keyboard-input-in-a-script-from-the-termina
oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

try:
    while 1:
        try:
            c = sys.stdin.read(1)
            if c:
                if c == 't':
                    dumpTime()
        except IOError: pass
        time.sleep(0.01)
finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
