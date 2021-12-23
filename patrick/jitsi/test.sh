#!/bin/bash -eu -o pipefail

export AWS_DEFAULT_REGION=ap-southeast-2
export AWS_REGION=$AWS_DEFAULT_REGION

INSTANCE_PROFILE=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`InstanceProfile`].OutputValue' --output text)
SECURITY_GROUP=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`SecurityGroup`].OutputValue' --output text)


aws ec2 run-instances --image-id "ami-0bf8b986de7e3c7ce" \
  --instance-type "t3.micro" \
  --security-group-ids "${SECURITY_GROUP}" \
  --user-data file://ec2-userdata.yaml \
  --associate-public-ip-address \
  --subnet-id subnet-33af5c55 \
  --iam-instance-profile "Name=jitsi-role-InstanceProfile-${INSTANCE_PROFILE}" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value='$1'},{Key=owner,Value='patrick'},{Key='letsencrypt:email',Value='$2'}]" 
