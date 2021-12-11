#!/bin/bash

aws ec2 run-instances --image-id "ami-0bf8b986de7e3c7ce" --key-name "ec2-relays" --instance-type "t3.micro" --security-group-ids sg-02ca38382a32fd1eb --user-data file://ec2-pycon-install-relay.sh --associate-public-ip-address --tag-specifications "ResourceType=instance,Tags=[{Key=i-type,Value=ingest-relay},{Key=i-room,Value=$1},{Key=Name,Value='RTMP Relay $1'}]" --subnet-id subnet-33af5c55 --iam-instance-profile "Name=NDV-EC2Role" --block-device-mappings file://relay-ebs-mapping.json
