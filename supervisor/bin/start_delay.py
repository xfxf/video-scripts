#!/usr/bin/env python
#
# Hackish script to start supervisor processes in an ordered and timely fashion

import sys
import time
import xmlrpclib

SERVER_HOST = 'http://localhost:9001/RPC2'
delay = 0


def usage():
    print "{} <delay> program [program ...]".format(sys.argv[0])
    exit(1)

if len(sys.argv) < 2:
    usage()
try:
    delay = int(sys.argv[1])
except:
    usage()


try:
    server = xmlrpclib.Server(SERVER_HOST)
    if server is not None:
        state = server.supervisor.getState()
        print "{} is {} ".format(server.supervisor.getIdentification(), state['statename'])
        if state['statecode'] != 1:
            exit(2)
    else:
        print "Communication error with supervisord"
        exit(2)
except Exception as exc:
    print "ERROR: {}".format(exc)
    exit(2)


for n in range(2, len(sys.argv)):
    # get information about the named process
    procname = sys.argv[n]
    try:
        procinfo = server.supervisor.getProcessInfo(procname)
        # do the sleep
        time.sleep(delay)
        if procinfo['state'] not in [0]:
            print "Process {}:{} is not stopped: state={}".format(procinfo['group'], procinfo['name'], procinfo['statename'])
        else:
            if server.supervisor.startProcess(procname):
                print "Started {}:{}".format(procinfo['group'], procinfo['name'])
            else:
                print "Error starting {}:{}".format(procinfo['group'], procinfo['name'])
    except xmlrpclib.Fault as exc:
        print "Process named {} - {}".format(procname, exc.faultString)
    except Exception as exc:
        print "WARNING: process={} - {}".format(procname, exc)


