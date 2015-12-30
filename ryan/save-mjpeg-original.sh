# this worked under Ubuntu 14.04 LTS, does not work under Ubuntu 15.10 LTS

gst-launch-1.0 v4l2src device=/dev/video0 ! image/jpeg,width=1280,height=720 ! capssetter caps='image/jpeg,width=1280,height=720,framerate=25/1' ! matroskamux name=mux alsasrc device='hw:0,0' ! audio/x-raw,channels=2,rate=48000 ! audioconvert ! vorbisenc ! queue ! mux. mux. ! queue max-size-bytes=100000000 max-size-time=0 ! filesink location=hdmi2usb_recording_`date +%s`.mkv



