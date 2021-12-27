#!/bin/bash -eu

set -o pipefail

source ../common-jitsi-jibri.sh
source ../jitsi-jibri-role/role-helpers.sh

INSTANCE_PROFILE=$(get_instance_profile)
SECURITY_GROUP=$(get_jitsi_security_group)

aws ec2 run-instances --image-id "ami-0bf8b986de7e3c7ce" \
  --instance-type "t3.micro" \
  --security-group-ids "${SECURITY_GROUP}" \
  --user-data file://jitsi-userdata.yaml \
  --associate-public-ip-address \
  --subnet-id "${SUBNET_ID}" \
  --iam-instance-profile "Name=${INSTANCE_PROFILE}" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value='$1'},{Key=owner,Value='patrick'},{Key='letsencrypt:email',Value='$2'}]" 
