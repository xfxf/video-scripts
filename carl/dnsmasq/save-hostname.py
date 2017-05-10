#!/usr/bin/python

# save-hostname.py - called from dnsmasq --dhcp-script=save-hostname.py

"""
man dnsmasq
--dhcp-script=<path>
  Whenever a new DHCP lease is created, or an old  one  destroyed,
  or  a  TFTP file transfer completes, the executable specified by
  this option is run.  <path> must be  an  absolute  pathname,  no
  PATH  search  occurs.   The  arguments to the process are "add",
  "old" or "del", the MAC address of the host (or DUID for IPv6) ,
  the  IP address, and the hostname, if known. "add" means a lease
  has been created, "del" means it has been destroyed, "old" is  a
  notification  of  an  existing  lease  when  dnsmasq starts or a
  change to MAC address or hostname of an  existing  lease  (also,
  lease  length  or expiry and client-id, if leasefile-ro is set).
  If the MAC address is from a network type other  than  ethernet,
  it    will    have    the    network    type    prepended,    eg
  "06-01:23:45:67:89:ab" for token ring. The  process  is  run  as
  root  (assuming that dnsmasq was originally run as root) even if
  dnsmasq is configured to change UID to an unprivileged user.

  The environment is inherited from the invoker of  dnsmasq,  with
  some or all of the following variables added

  If the client provides a hostname, DNSMASQ_SUPPLIED_HOSTNAME

    dhcp-host=&lt;mac&gt;,&lt;ip&gt;,&lt;hostname&gt
    /etc/dnsmasq.d/, which is included in my dnsmasq conf:  dn    smasq ... --conf-dir=/etc/dnsmasq.d
"""

import argparse
import os

DEBUG=True

def ck_file(args):

    """
    look for lines that don't begin with # or [
    hope they start with a hostname
    take the first segment if they are a FQDN
    """

    try:
        for l in open(args.filename).read().split('\n'):
            if l.startswith("dhcp-host="):
                values=l.split('=')[1]
                mac,ip,hostname = values.split(',')
                if mac == args.mac:
                    return True
    except IOError:
        return False

    return False

def add_to_file(args):
    with open(args.filename,'a') as f:
        line="\ndhcp-host={mac},set:{hostname},{hostname}\n".format(
                mac=args.mac, ip=args.ip, hostname=args.hostname)
        f.write(line)

def hup_server():
    pass

def add_maybe(args):

    """
    if there is a hostname to save
      and this is a new mac:
          add the mac:hostnampa.
    """

    if args.hostname is not None \
            and not ck_file(args):
        add_to_file(args)
        hup_server()


def get_args():

    """
    The  arguments to the process are
    "add", "old" or "del",
    the MAC address of the host (or DUID for IPv6) ,
    the  IP address,
    and the hostname, if known.
    """

    parser = argparse.ArgumentParser(
            description="""called from dnsmasq""")

    parser.add_argument('action',
            help='What the server is doing.')

    parser.add_argument('mac',
            help='MAC address of the host.')

    parser.add_argument('ip',
            help='ip addresst.')

    parser.add_argument('hostname',
            nargs='?',
            default=None)

    parser.add_argument('--filename',
            default="/etc/dnsmasq.d/macs.cfg",
            help='File to save mac/hostnames (overide for testing)')

    args = parser.parse_args()

    return args


def main():
    args = get_args()

    if DEBUG:
	with open('/tmp/foo','a') as f:
	    f.write(args.__repr__())
	    f.write('\n')
            # f.write(os.getenv('DNSMASQ_SUPPLIED_HOSTNAME', "oh no!"))
	    # f.write('\n')

    if args.action == "add":
        add_maybe(args)


if __name__ == "__main__":
    main()


