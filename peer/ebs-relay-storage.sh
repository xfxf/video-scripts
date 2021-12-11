#!/bin/bash

aws ec2 create-volume --availability-zone ap-southeast-2b --no-encrypted --volume-type sc1 --size 500 --tag-specifications "ResourceType=volume,Tags=[{Key=i-type,Value=ingest-store},{Key=i-room,Value=$1},{Key=Name,Value='RTMP Storage $1'}]"
