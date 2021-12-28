1. Figure out a way to try session manager until its ready after starting

2. Configure the jitsi box automatically - start recording still shows in the UI.

# sudo nano /etc/jitsi/meet/`hostname`-config.js
# fileRecordingsEnabled -> true
# liveStreamingEnabled: true,
# hiddenDomain: "jibri-test-5.aws.nextdayvideo.com.au",


3. Somthing about buttons in the UI

Also make sure that in your interface config (/usr/share/jitsi-meet/interface_config.js by default), the TOOLBAR_BUTTONS array contains the recording value if you want to show the file recording button and the livestreaming value if you want to show the live streaming button.

