#!/bin/bash -eu

set -o pipefail

export AWS_DEFAULT_REGION=ap-southeast-2
export AWS_REGION=$AWS_DEFAULT_REGION

STACK_NAME=jitsi-role
INSTANCE_PROFILE=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs[?OutputKey==`InstanceProfile`].OutputValue' --output text)

packer build \
  -var instance_profile="$INSTANCE_PROFILE" \
  jibri.pkr.hcl
