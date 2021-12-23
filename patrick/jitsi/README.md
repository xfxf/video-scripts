# jitsi tests

## role & security group

The role cloudformation stack (`jitsi-role`) should already exist, but `./deploy-role.sh` will make sure it's up to date.

## create a server

`./test.sh servername email@somewhere`

`servername` will create a machine named `servername.aws.nextdayvideo.com.au` including DNS entries.

`email@somewhere` is used so that the machine gets a lets encrypt certificate for that `https://` goodness.

## connecting

Use AWS Session Manager, e.g. `aws ssm start-session --target INSTANCE_ID`

## clean up

Terminate the instance `aws ec2 terminate-instances --instance-id INSTANCE_ID`.

You'll need to clean up the Route 53 record as well (if you're creating a new server you can just reuse the name instead, but watch out for DNS caching - the default TTL is 60 seconds which isn't too bad)
