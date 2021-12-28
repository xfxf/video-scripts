#!/bin/bash -eu

set -o pipefail

source ../../common-jitsi-jibri.sh
source ../../jitsi-jibri-role/role-helpers.sh

INSTANCE_PROFILE=$(get_instance_profile)
JIBRI_SECURITY_GROUP=$(get_jibri_security_group)
JIBRI_IMAGE_ID="ami-0999e9a31f4944d9f"

if [ "$#" -ne 1 ]; then
    echo Usage: $0 jitsi-host-name
    echo "Note: jitsi-host-name should not be the complete host name (e.g. do not include the .aws.nextdayvideo.com.au)"
    exit 1
fi

JITSI_MEET_HOST=$1

JITSI_MEET_HOST_STATE=$(aws ec2 describe-instances --filters Name=tag:Name,Values="$JITSI_MEET_HOST" --query Reservations[].Instances[].State.Name --output text)

if [[ "running" != "$JITSI_MEET_HOST_STATE" ]]; then
  echo "$JITSI_MEET_HOST is ${JITSI_MEET_HOST_STATE:-not found}, did you use the correct host?"
  exit 1
fi

NODE_NAME=${JITSI_MEET_HOST}-jibri-$(uuidgen | cut -d'-' -f1)
AWS_WHOAMI=$(aws sts get-caller-identity --query Arn --output text | rev | cut -d'/' -f 1 | rev)

echo "Name: $NODE_NAME, owner: $AWS_WHOAMI, JitsiMeetHost: $JITSI_MEET_HOST"

INSTANCE_ID=$(aws ec2 run-instances --image-id "$JIBRI_IMAGE_ID" \
  --instance-type "c6i.2xlarge" \
  --security-group-ids "${JIBRI_SECURITY_GROUP}" \
  --user-data file://jibri-userdata.yaml \
  --associate-public-ip-address \
  --subnet-id "${SUBNET_ID}" \
  --iam-instance-profile "Name=${INSTANCE_PROFILE}" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value='$NODE_NAME'},{Key=owner,Value='$AWS_WHOAMI'},{Key=JitsiMeetHost,Value='$JITSI_MEET_HOST.aws.nextdayvideo.com.au'}]" \
  --query Instances[].InstanceId \
  --output text)

echo "Started $INSTANCE_ID, waiting for the instance to be report in to AWS Systems Manager..."
echo "Please remember that this instance will cost \$250/month if left running!"

get_ping_status() {
  aws ssm describe-instance-information --filters Key=InstanceIds,Values="$1" --query InstanceInformationList[].PingStatus --output text
}

LAST_PING_STATUS=$(get_ping_status $INSTANCE_ID)

while [ "${LAST_PING_STATUS:-none}" != "Online" ]; do
  echo "Last status ${LAST_PING_STATUS:-none}, waiting for Online..."
  sleep 5
  LAST_PING_STATUS=$(get_ping_status $INSTANCE_ID)
done

echo "Instance is now online."
echo "Connect: aws ssm start-session --target $INSTANCE_ID"
echo "Terminate: aws ec2 terminate-instances --instance-id $INSTANCE_ID"
