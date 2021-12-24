1. Recordings, finalize script (_or_ disable recordings)

2. Add a security group for the jibri boxes, allow `5222` from jibri -> jitsi only

3. Remove the 2222 ingress rule (its for testing jibri), and make sure it doesn't break anything

2. Configure the jitsi box automatically:

# /etc/jitsi/jicofo/jicofo.conf
# defaults to recorder.jitsi-meet-tests8.aws.nextdayvideo.com.au

# /etc/prosody/conf.d/jibri-test-5.aws.nextdayvideo.com.au.cfg.lua to add:

# VirtualHost "jibri-test-5.aws.nextdayvideo.com.au"
#   modules_enabled = {
#     "ping";
#   }
#   authentication = "internal_plain"

# to /etc/prosody/conf.avail/HOSTNAME.cfg.lua on the jitsi-meet box

# sudo systemctl reload prosody

## Create the passwwords

Using `aws secretsmanager get-random-password --output text`

Then 

```
sudo prosodyctl register jibri auth.jitsi-meet-tests8.aws.nextdayvideo.com.au "..."
sudo prosodyctl register recorder jibri-test-5.aws.nextdayvideo.com.au "..."
```

# sudo nano /etc/jitsi/meet/`hostname`-config.js
# fileRecordingsEnabled -> true
# liveStreamingEnabled: true,
# hiddenDomain: "jibri-test-5.aws.nextdayvideo.com.au",

# write SSM

to `/jitsi/${HOSTNAME}` with 

```
{"control":{"domain":"auth.jitsi-meet-tests8.aws.nextdayvideo.com.au","username":"jibri","password:"..."},"call":{"domain":"jibri-test-5.aws.nextdayvideo.com.au","username":"recorder","password":"..."}}
```

