#!/bin/bash -eu

set -o pipefail

export AWS_DEFAULT_REGION=ap-southeast-2
export AWS_REGION=$AWS_DEFAULT_REGION

STACK_NAME=jitsi-role
INSTANCE_PROFILE=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`InstanceProfile`].OutputValue' --output text)
SECURITY_GROUP=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`SecurityGroup`].OutputValue' --output text)

JIBRI_IMAGE_ID="ami-0999e9a31f4944d9f"

aws ec2 run-instances --image-id "$JIBRI_IMAGE_ID" \
  --instance-type "c6i.2xlarge" \
  --security-group-ids "${SECURITY_GROUP}" \
  --user-data file://jibri-userdata.yaml \
  --associate-public-ip-address \
  --subnet-id subnet-33af5c55 \
  --iam-instance-profile "Name=${INSTANCE_PROFILE}" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value='$1'},{Key=owner,Value='patrick'},{Key='letsencrypt:email',Value='$2'},{Key=JitsiMeetHost,Value='$3'}]" 

echo "Please remember that this instance will cost $250/month if left running!"
