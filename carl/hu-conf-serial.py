#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import time
import serial

rtscts = True
read_timeout = 10.0
linewaittime = 0.3
waittime = 0.1
inter_byte_timeout = 1.0

prompt = b'HDMI2USB>'


def sendbytes(sport, bytes2send):
    print(str.encode(bytes2send), end="")
    for ch in bytes2send:
        sport.write(ch)
        time.sleep(waittime)
    time.sleep(linewaittime)


def readbytes(sport, waitfor):
    length = len(waitfor)
    bytes_read = b''
    matched = False
    ch = 0
    while ch != '\n':
        ch = sport.read()
        if bytes_read[:length] == waitfor:
            matched = True
            break
        bytes_read += ch
    print(str.encode(bytes_read), end="")
    return matched


def expect(sport, waitfor, bytes2send = None):
    while not readbytes(sport, waitfor):
        pass
    if bytes2send is not None:
        sendbytes(sport, bytes2send)


def send(filename, port, speed):
    sport = serial.Serial(port = port, baudrate=speed, parity=serial.PARITY_NONE,
                          stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                          rtscts=rtscts, timeout=read_timeout, inter_byte_timeout=inter_byte_timeout)
    sport.isOpen()
    sport.setDTR()
    sendbytes(sport, b'\r\n')

    with open(filename) as f:
        for line in f.readlines():
            expect(sport, prompt, str.encode(line))
            time.sleep(waittime)
        f.close()

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('port', default = "/dev/ttyAMC0", help="serial port" ) # /dev/ttyVIZ0
    parser.add_argument('speed', default = 115200, help = "serial baud rate")
    parser.add_argument('filename', help="input filename" )
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    send(args.filename, args.port, args.speed)

if __name__ == '__main__':
    main()
