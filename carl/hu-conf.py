#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pexpect
import sys
import argparse
import time


def send(filename,port):

# Note that, for Python 3 compatibility reasons, we are using spawnu and
# importing unicode_literals (above). spawnu accepts Unicode input and
# unicode_literals makes all string literals in this script Unicode by default.

    child = pexpect.spawnu(
    		'flterm --port {port} --speed 115200'.format(port=port))
    child.logfile = sys.stdout

    child.sendline('')
    child.expect('HDMI2USB>')

    for line in open(filename).read().split('\n'):
        child.sendline( line )
        child.expect('HDMI2USB>')
        time.sleep(.1)

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('port', default = "/dev/ttyAMC0", help="serial port" ) # /dev/ttyVIZ0
    parser.add_argument('filename', help="input filename" )
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    send(args.filename, args.port)

if __name__ == '__main__':
    main()

