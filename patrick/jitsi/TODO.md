1. Figure out a way to try session manager until its ready after starting

2. Remove the 2222 ingress rule (its for testing jibri), and make sure it doesn't break anything

3. Configure the jitsi box automatically - start recording still shows in the UI.

# sudo nano /etc/jitsi/meet/`hostname`-config.js
# fileRecordingsEnabled -> true
# liveStreamingEnabled: true,
# hiddenDomain: "jibri-test-5.aws.nextdayvideo.com.au",
