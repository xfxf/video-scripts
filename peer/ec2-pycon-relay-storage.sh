#!/bin/bash

aws ec2 create-volume --availability-zone us-east-2b --no-encrypted --volume-type gp2 --size 250 --tag-specifications "ResourceType=volume,Tags=[{Key=i-type,Value=ingest-store},{Key=i-room,Value=$1},{Key=Name,Value='RTMP Storage $1'}]" 