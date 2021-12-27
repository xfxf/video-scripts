#!/bin/bash -eu

set -o pipefail

source ../../common-jitsi-jibri.sh
source ../../jitsi-jibri-role/role-helpers.sh

INSTANCE_PROFILE=$(get_instance_profile)
JIBRI_SECURITY_GROUP=$(get_jibri_security_group)
JIBRI_IMAGE_ID="ami-0999e9a31f4944d9f"

aws ec2 run-instances --image-id "$JIBRI_IMAGE_ID" \
  --instance-type "c6i.2xlarge" \
  --security-group-ids "${JIBRI_SECURITY_GROUP}" \
  --user-data file://jibri-userdata.yaml \
  --associate-public-ip-address \
  --subnet-id subnet-33af5c55 \
  --iam-instance-profile "Name=${INSTANCE_PROFILE}" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value='$1'},{Key=owner,Value='patrick'},{Key=JitsiMeetHost,Value='$2'}]" 

echo "Please remember that this instance will cost $250/month if left running!"
