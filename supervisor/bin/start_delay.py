#!/usr/bin/env python
#
# Hackish script to start supervisor processes in an ordered and timely fashion

import sys
import time
import xmlrpclib

SERVER_HOST='http://localhost:9001/RPC2'

def usage():
    print "{} <delay> program [program ...]".format(sys.argv[0])
    exit(1)

if len(sys.argv) < 2:
    usage()
try:
    delay=int(sys.argv[1])
except:
    usage()


try:
    server = xmlrpclib.Server(SERVER_HOST)
    if server:
        state = server.getState()
        print "{} is {} ".format(server.getIdentification(), state['statename'])
        if state['statecode'] != 1:
            exit(2)
    else:
        print "Communication error with supervisord"
        exit(2)
except:
    print "Could not access supervisord"
    exit(2)


for n in range(2, len(sys.argv)):
    # get information about the named process
    procname = sys.argv[n]
    procinfo = server.getProcessInfo(procname)
    if procinfo:
        # do the sleep
        time.sleep(delay)
        print "Doing something with {}:{}, state {}".format(procinfo['group'], procinfo['name'], procinfo['statename'])
    else:
        print "Process named {} not found".format(procname)


