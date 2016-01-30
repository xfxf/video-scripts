#!/usr/bin/env python3
#

import argparse
from opsis.hdmi2usb import *

def get_args():
    parser = argparse.ArgumentParser(description='Monitor Opsis debug output')
    parser.add_argument('--port', default=Hdmi2Usb.PORT_DEFAULTS['port'], required=False, help="serial port" )
    parser.add_argument('--speed', default=Hdmi2Usb.PORT_DEFAULTS['baudrate'], required=False, help="serial baud rate")
    parser.add_argument('--input', default='input0', required=False, help="specify input to debug")
    args = parser.parse_args()
    return args


def print_debug(line):
    print("> " + bytes.decode(line), end='')

def monitor(errs, res):
    print("{} Res = {}".format('Errors' if errs else 'Good', res))


def main():
    args = get_args()
    hdmi2usb = Hdmi2Usb(port = args.port, input = args.input)
    hdmi2usb.sampler(monitor)


if __name__ == '__main__':
    main()
