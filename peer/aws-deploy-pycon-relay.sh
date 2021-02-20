#!/bin/bash

aws ec2 run-instances --region us-east-2 --image-id "ami-02aa7f3de34db391a" --key-name "ec2-relays-us" --instance-type "t2.micro" --security-group-ids sg-0cbf07f22f4f0cfc7 --user-data file://ec2-pycon-install-relay.sh --associate-public-ip-address --tag-specifications "ResourceType=instance,Tags=[{Key=i-type,Value=ingest-relay},{Key=i-room,Value=$1},{Key=Name,Value='RTMP Relay $1'}]" --credit-specification CpuCredits=standard --subnet-id subnet-38519f53 --iam-instance-profile "Name=NDV-EC2Role"
