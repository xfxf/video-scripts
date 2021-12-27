#!/bin/bash -eu -o pipefail

cd $(dirname "$0")

source ../common-jitsi-jibri.sh
source ./role-helpers.sh

aws cloudformation deploy \
  --template-file role.cfn.yaml \
  --stack-name "$ROLE_STACK_NAME" \
  --capabilities CAPABILITY_IAM

INSTANCE_PROFILE=$(get_instance_profile)
SECURITY_GROUP=$(get_jitsi_security_group)
JIBRI_SECURITY_GROUP=$(get_jibri_security_group)

echo "Instance Profile: $INSTANCE_PROFILE"
echo "Security Group: $SECURITY_GROUP"
echo "JIBRI_SECURITY_GROUP: $JIBRI_SECURITY_GROUP"
