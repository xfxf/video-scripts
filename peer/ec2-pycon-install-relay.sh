#!/bin/bash

####################################################
# install-relay.sh - cloud-init user-data version  #
#  v0.1.3d charlie clownfish - storage volumes v2  #
#                                                  #
# Designed for use with AWS EC2!                   #
#                                                  #
# Usage: Use this script as user-data              #
#                                                  #
# Params: N/A                                      #
#          !! These tags  are REQUIRED !!          #
#   Tags: i-type(str): relay type identifier [DNS] #
#         i-room(int): room number [DNS]           #
# Config: NGINX_VERSION: nginx version number      #
#         ZONE_ID: AWS Route53 Zone ID, for CNAMEs #
#         DOMAIN_NAME: Take a guess, pal.          #
####################################################

NGINX_VERSION="1.19.1" # Currently only tested with 1.19.1, but anything 1.13+ should work
ZONE_ID="Z09102521YXWQT2ZKMPP7"
DOMAIN_NAME="aws.nextdayvideo.com.au"

apt -y update
DEBIAN_FRONTEND=noninteractive apt -y full-upgrade # apt is silly
DEBIAN_FRONTEND=noninteractive apt -y install build-essential git awscli curl jq libssl-dev

echo "Gathering data..."
cd /root
mkdir .aws
cat <<tac > .aws/config
[default]
region = ap-southeast-2
tac
INSTANCE_ID=`curl -s http://instance-data/latest/meta-data/instance-id`
aws ec2 describe-tags --region ap-southeast-2 --filters "Name=resource-id,Values=$INSTANCE_ID" > instance-tags.json
INSTANCE_TYPE=`jq -r '.Tags[]| select(.Key == "i-type")|.Value' instance-tags.json`
ROOM_NUMBER=`jq -r '.Tags[]| select(.Key == "i-room")|.Value' instance-tags.json`
PUB_HOSTNAME=`curl -s http://instance-data/latest/meta-data/public-hostname`
VIDEO_VOLID=`aws ec2 describe-volumes | jq -r ".Volumes[]|select(.AvailabilityZone==\"ap-southeast-2b\")|select(.Tags)|select(.Tags[].Value==\"ingest-store\")|select(.Tags[].Value==\"$ROOM_NUMBER\").VolumeId"`

echo "$INSTANCE_ID"
echo "$INSTANCE_TYPE"
echo "$ROOM_NUMBER"
echo "$PUB_HOSTNAME"
echo "$VIDEO_VOLID"

echo "Moving to Working directory"
mkdir /root/src
cd /root/src

echo "Getting src.."
wget "http://nginx.org/download/nginx-$NGINX_VERSION.tar.gz"
git clone https://github.com/sergey-dryabzhinsky/nginx-rtmp-module.git

tar xf "nginx-$NGINX_VERSION.tar.gz"
rm "nginx-$NGINX_VERSION.tar.gz"
cd "nginx-$NGINX_VERSION/"
./configure --add-module=../nginx-rtmp-module --prefix=/opt/nginx --without-http_charset_module --without-http_gzip_module --without-http_ssi_module --without-http_userid_module --without-http_access_module --without-http_auth_basic_module --without-http_mirror_module --without-http_autoindex_module --without-http_geo_module --without-http_map_module --without-http_split_clients_module --without-http_referer_module --without-http_rewrite_module --without-http_proxy_module --without-http_fastcgi_module --without-http_uwsgi_module --without-http_scgi_module --without-http_grpc_module --without-http_memcached_module --without-http_limit_conn_module --without-http_limit_req_module --without-http_empty_gif_module --without-http_browser_module --without-http_upstream_hash_module --without-http_upstream_ip_hash_module --without-http_upstream_least_conn_module --without-http_upstream_random_module --without-http_upstream_keepalive_module --without-http_upstream_zone_module --without-http-cache --without-pcre

make
make install

cd /opt/nginx/conf
rm -rfv *
cp "/root/src/nginx-$NGINX_VERSION/conf/mime.types" .
cat <<tac > nginx.conf
worker_processes  1;
error_log  logs/error.log;

events {
	worker_connections  1024;
}


http {
	include       mime.types;
	default_type  text/plain;

	access_log  logs/access.log;

	server {
		listen       80;
		server_name  _;
		location /room-stat {
			rtmp_stat all;
		}
	}
}
rtmp {
	server {
		listen 1935;
		live on;
		session_relay on;
		application room-push {
tac

#curl -s http://www.gstatic.com/ipranges/cloud.json | jq -r '.prefixes|.[]|select(.scope == "us-central1")|"\t\t\tallow publish " + .ipv4Prefix + ";"' >> nginx.conf

cat <<tac >> nginx.conf
			allow publish all;
			allow play all;
			record all;
			record_path /video;
			record_suffix _%Y-%m-%d_%H_%M_%S.flv;
			record_interval 30m;
		}
	}
}
tac

cd /root
cat <<tac > upsert.json
{
	"Comment": "UPSERT room ingest dns",
	"Changes": [{
		"Action": "UPSERT",
		"ResourceRecordSet": {
			"Name": "rtmp-$INSTANCE_TYPE-r$ROOM_NUMBER.$DOMAIN_NAME",
			"Type": "CNAME",
			"TTL": 60,
			"ResourceRecords": [{ "Value": "$PUB_HOSTNAME"}]
		}
	}]
}
tac
aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID --change-batch file://upsert.json

mkdir /video

aws ec2 detach-volume --volume-id $VIDEO_VOLID
aws ec2 attach-volume --volume-id $VIDEO_VOLID --instance-id $INSTANCE_ID --device /dev/xvdf

echo "/dev/xvdf /video ext4 defaults 0 0" | tee -a /etc/fstab

cd /opt/nginx
sbin/nginx -t

curl -X POST -H 'Content-type: application/json' --data "{'text':'New Instance \`$INSTANCE_ID\` of type \`$INSTANCE_TYPE\` spun up, \`rtmp://rtmp-$INSTANCE_TYPE-r$ROOM_NUMBER.$DOMAIN_NAME/room-push/room$ROOM_NUMBER\`'}" https://hooks.slack.com/services/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

rm /root/upsert.json /root/instance-tags.json

cat <<tac > /etc/systemd/system/nginx-rtmp.service
[Unit]
Description=The NGINX HTTP and reverse proxy server
After=syslog.target network-online.target remote-fs.target nss-lookup.target
Wants=network-online.target

[Service]
Type=forking
PIDFile=/opt/nginx/logs/nginx.pid
ExecStartPre=/opt/nginx/sbin/nginx -t
ExecStart=/opt/nginx/sbin/nginx
ExecReload=/opt/nginx/sbin/nginx -s reload
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
tac
systemctl daemon-reload
systemctl enable --now nginx-rtmp.service
