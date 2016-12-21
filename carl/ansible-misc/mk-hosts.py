#!/usr/bin/python

# mk-hosts.py - Makes /etc/hosts entries from ips found in juju status

import argparse
import json
import subprocess


def get_status():
    p=subprocess.Popen(['juju', 'status', '--format', 'json'], stdout=subprocess.PIPE)
    sout,serr = p.communicate()
    return sout
       
def parse_status(s):

    """
    given juju stats as json
    dig out the names and ip addresses
    return a list of ip,app (ia)
    """

    # app name is the name assinged to a container.
    # assume it relates to the host name found in ansible hosts file

    j = json.loads(s)

    apps = j['applications']

    ias = []
    for app in apps:
        ip = apps[app]['units']['{}/0'.format(app)]['public-address']
        ias.append((ip,app))

    return ias

def mk_hosts(ias,dom):
    """
    given a list of ip,app names and optional doman name
    return a list of ip,hostname
    """

    if dom:
        hosts = []
        for ip,app in ias:
              hosts.append((ip, '{app}.{dom}'.format(app=app, dom=dom)))
    else:
        hosts = ias

    return hosts

def mk_hostlines(hosts):

    """ 
    Given a list of ip,host
    make /etc/hosts lines 
    """

    for host in hosts:
        print('{}\t{}'.format(*host)) 


def allow_root(hosts):

    """
    Enable root login
    using the same keys setup for username ubuntu 
    ssh into each host, copy ~/.ssh/authorized_keys to /root/.ssh
    """
# ssh ubuntu@streambackend3.video.fosdem.org "sudo cp .ssh/authorized_keys /root/.ssh
    for ip,host in hosts:
        cmd=['ssh', 'ubuntu@{host}'.format(host=host), 
               "sudo", "cp", ".ssh/authorized_keys", "/root/.ssh"]
        print(cmd)
        p=subprocess.Popen(cmd, stdout=subprocess.PIPE)
        sout,serr = p.communicate()

def get_args():

    parser = argparse.ArgumentParser(
            description="""Make lines for /etc/hosts""")
 
    parser.add_argument('--domain-name', 
            help='suffix to be appended to app names to make FQDN')

    parser.add_argument('--allow-root', action='store_true',
            help="run allow_root(hosts) "
             "(do this once all the containers are ready)" )

    parser.add_argument('-v', '--verbose', action='count', default=0,
            help="Also print INFO and DEBUG messages.")

    args = parser.parse_args()

    return args


def main():
    args = get_args()
    s = get_status()
    ais = parse_status(s)
    # hosts = mk_hosts(ais, "video.fosdem.org")
    hosts = mk_hosts(ais, args.domain_name)
    mk_hostlines(hosts)

    if args.allow_root: 
        allow_root(hosts)

if __name__ == "__main__":
    main()
        

