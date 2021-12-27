1. Recordings, finalize script (_or_ disable recordings)

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



```
   19  cd /etc/
   21  cd prosody/
   23  cd conf.avail/

   27  sudo vim /etc/prosody/conf.avail/jitsi-meet-tests8.aws.nextdayvideo.com.au.cfg.lua
   36  sudo vim /etc/jitsi/meet/`hostname`-config.js
   74  sudo vim /etc/prosody/conf.avail/`hostname`.cfg.lua
   52  sudo vim /etc/prosody/prosody.cfg.lua 
   28  cat prosody.cfg.lua | grep c2s_require_encryption

   67  sudo vim /etc/jitsi/jicofo/jicofo.conf

   28  sudo systemctl reload prosody
   41  sudo systemctl restart jicofo
   42  sudo systemctl restart jitsi-videobridge2

   48  sudo prosodyctl register jibri auth.jitsi-meet-tests8.aws.nextdayvideo.com.au "..."
   55  prosodyctl register recorder jibri-test-5.aws.nextdayvideo.com.au "..."

   50  sudo tail -f /var/log/jitsi/jicfofo.log /var/log/jitsi/jvb.log /var/log/prosody/prosody.err /var/log/prosody/prosody.log

   as root:
```