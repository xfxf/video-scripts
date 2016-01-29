#!/usr/bin/python

import shutil
import subprocess


known = {
    'r1mix':  '94:de:80:77:68:33',
    'r2mix':  '14:da:e9:33:b2:4c',
    'r7mix':  '54:ee:75:12:2f:f6',
    'r7cam':  'f0:de:f1:49:72:60',
    'r7grab': '00:1e:37:90:15:7f',
}


def enumerate_machines():
    for room in (1, 2, 3, 4, 5, 7):
        for i, box in enumerate(('mix', 'cam', 'grab')):
            ip = '192.168.0.%i%i' % (room, i)
            name = 'r%i%s' % (room, box)
            yield ip, name

with open('dhcpd-macs.conf', 'w') as f:
    for ip, name in enumerate_machines():
        f.write(
            'host %(name)s {\n'
            '    hardware ethernet %(mac)s;\n'
            '    fixed-address %(ip)s;\n'
            '    option host-name "%(name)s";\n'
            '}\n\n'
            % {
                'name': name,
                'mac': known.get(name, '00:00:00:00:00:00'),
                'ip': ip,
            })

with open('hosts', 'w') as f:
    f.write('127.0.0.1\tlocalhost\n\n')
    f.write('192.168.0.1\tavserver.private avserver\n\n')

    for ip, name in enumerate_machines():
        f.write(
            '%(ip)s\t%(name)6s.private %(name)s\n'
            % {
                'name': name,
                'ip': ip,
            })
    f.write('''\n
# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
''')

for ip, name in enumerate_machines():
	with open('{}.conf'.format(name), 'w') as f:
		f.write(
			"""[connection]
id={ip}
uuid=@UUID@
type=802-3-ethernet

[ipv4]
method=manual
addresses1={ip};8;0.0.0.0;
dns=192.168.0.1;
dns-search=private

[802-3-ethernet]
duplex=full

[ipv6]
method=ignore
""".format(ip=ip) )



shutil.copyfile('dhcpd-macs.conf', '/etc/dhcp/dhcpd-macs.conf')
subprocess.check_output(('service', 'isc-dhcp-server', 'restart'))

# vi: set et sw=4 ts=4:
