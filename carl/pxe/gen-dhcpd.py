#!/usr/bin/python

import shutil
import subprocess


known = {
	"r1mix":  "54:ee:75:1a:2d:22",
	"r1cam":  "f0:de:f1:49:04:a8",
	"r1grab": "f0:de:f1:49:04:e5",
	
        'r2mix':  '54:ee:75:20:90:78',
        "r2grab": "f0:de:f1:49:04:e2",
	"r2cam":  'f0:de:f1:49:72:60',

	"r3mix":  "54:ee:75:19:05:7e",
        "r3cam":  "f0:de:f1:49:05:1b",
	"r3grab": "f0:de:f1:3e:8d:ae",
 
	"r4mix":  "54:ee:75:1d:54:c7",
        "r4cam":  "f0:de:f1:49:72:35",
	"r4grab": "00:1c:25:b8:bb:cc",
 
        'r5mix':  '54:ee:75:12:2f:f6',
        "r5cam":  "f0:de:f1:49:04:62",
	"r5grab": "00:1e:37:90:15:7f",

     # 'r7mix': '00:1e:37:90:15:7f',
     'r7grab': '00:1e:37:90:17:77',
     'r7cam': 'f0:de:f1:49:04:ce',
}

snowflakes = {
    'r1cam2':  {'mac': '94:de:80:77:68:33', 'ip': '192.168.0.3'},
    'r1cam3':  {'mac': '14:da:e9:33:b2:4c', 'ip': '192.168.0.4'},
}

        # 'r2mix':  '14:da:e9:33:b2:4c', # desktop
	# "r1cam": "00:1e:37:84:1d:09", # desktop

def enumerate_machines():
    for room in (1, 2, 3, 4, 5, 7):
        for i, box in enumerate(('mix', 'cam', 'grab')):
            ip = '192.168.0.%i%i' % (room, i)
            name = 'r%i%s' % (room, box)
            yield ip, name

with open('dhcpd-macs.conf', 'w') as f:
    def one_dhcp(name,mac,ip):
        f.write(
            'host %(name)s {\n'
            '    hardware ethernet %(mac)s;\n'
            '    fixed-address %(ip)s;\n'
            '    option host-name "%(name)s";\n'
            '}\n\n'
            % {
                'name': name,
                'mac': mac,
                'ip': ip,
            })
    for ip, name in enumerate_machines():
        mac = known.get(name, '00:00:00:00:00:00')
        one_dhcp(name,mac,ip)
    for snowflake in snowflakes:
        one_dhcp(snowflake,
            snowflakes[snowflake]['mac'],
            snowflakes[snowflake]['ip']
           )

with open('hosts', 'w') as f:
    def one_host(name,ip):
        f.write(
            '%(ip)s\t%(name)6s.private %(name)s\n'
            % {
                'name': name,
                'ip': ip,
            })
 
    f.write('127.0.0.1\tlocalhost\n\n')
    f.write('192.168.0.1\tavserver.private avserver\n\n')

    for ip, name in enumerate_machines():
        one_host(name,ip)
    for snowflake in snowflakes:
        one_host(snowflake,
            snowflakes[snowflake]['ip']
           )


    f.write('''\n
# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
''')

def one_conf(ip):
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


for ip, name in enumerate_machines():
    def one_conf(ip):
     for snowflake in snowflakes:
        one_conf(snowflake,
            snowflakes[snowflake]['ip']
           )

shutil.copyfile('dhcpd-macs.conf', '/etc/dhcp/dhcpd-macs.conf')
subprocess.check_output(('service', 'isc-dhcp-server', 'restart'))

# vi: set et sw=4 ts=4:
