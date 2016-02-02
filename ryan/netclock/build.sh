gcc `pkg-config --cflags gstreamer-1.0` netclock-client.c -o netclock-client `pkg-config --libs gstreamer-1.0 gstreamer-net-1.0`
