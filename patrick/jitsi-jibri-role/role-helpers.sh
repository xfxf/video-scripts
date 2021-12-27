get_instance_profile() {
  aws cloudformation describe-stacks \
    --stack-name "$ROLE_STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`InstanceProfile`].OutputValue' \
    --output text
}

get_jitsi_security_group() {
  aws cloudformation describe-stacks \
    --stack-name "$ROLE_STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`SecurityGroup`].OutputValue' \
    --output text
}

get_jibri_security_group() {
  aws cloudformation describe-stacks \
    --stack-name "$ROLE_STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`JibriSecurityGroup`].OutputValue' \
    --output text
}