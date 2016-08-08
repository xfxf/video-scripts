# alter to work with gstreamer 1.6 (jpegdec/videoconvert) - not final

gst-launch-1.0 v4l2src device=/dev/video1 ! image/jpeg,width=1280,height=720 ! capssetter caps='image/jpeg,width=1280,height=720,framerate=25/1' ! jpegparse ! jpegdec ! videoconvert ! matroskamux ! filesink location=hdmi2usb_recording_`date +%s`.mkv



