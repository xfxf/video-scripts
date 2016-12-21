#!/usr/bin/python

# slurp-hosts.py - creates a contiainer for each host found in an ansible hosts file.

import argparse

def parse_hosts(filename):

    """
    look for lines that don't begin with # or [
    hope they start with a hostname
    take the first segment if they are a FQDN
    """

    hosts=set()
    for l in open(filename).read().split('\n'):
        if l.startswith(("#", "[")):
            continue
        if (l):
            h = l.split()[0].split('.')[0]
            hosts.add(h)

    return hosts


def print_jujus(hosts,charm):

    """ 
    stdout a bash script to create containers named after the hosts.
    and a few other things like show the status.
    """

    print('#!/bin/bash -ex')
    print('# juju add-model default')

    for h in hosts:
        print('juju deploy {charm} {host}'.format(charm=charm, host=h))
        print('juju config {host} hostname={host}'.format(host=h))

    print('juju status')



def get_args():

    parser = argparse.ArgumentParser(
            description="""Make lines for /etc/hosts""")
 
    parser.add_argument('filename', 
            help='path to ansible hosts file')

    parser.add_argument('-v', '--verbose', action='count', default=0,
            help="Also print INFO and DEBUG messages.")

    args = parser.parse_args()

    return args


def main():
    args = get_args()

    # hosts = parse_hosts('ansible/inventory/hosts')
    hosts = parse_hosts(args.filename)
    print_jujus(hosts,'/home/juser/temp/charm-ubuntu/builds/ubuntu')

if __name__ == "__main__":
    main()
        

