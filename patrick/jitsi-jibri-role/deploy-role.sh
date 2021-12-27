#!/bin/bash -eu -o pipefail

cd $(dirname "$0")

STACK_NAME=jitsi-role

export AWS_DEFAULT_REGION=ap-southeast-2
export AWS_REGION=$AWS_DEFAULT_REGION

aws cloudformation deploy \
  --template-file role.cfn.yaml \
  --stack-name "$STACK_NAME" \
  --capabilities CAPABILITY_IAM


INSTANCE_PROFILE=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`InstanceProfile`].OutputValue' --output text)
SECURITY_GROUP=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`SecurityGroup`].OutputValue' --output text)

echo "Instance Profile: $INSTANCE_PROFILE"
echo "Security Group: $SECURITY_GROUP"

# echo "::set-output name=frontendBucket::$FRONTEND_BUCKET"
