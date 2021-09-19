# subtitles streaming notes

* [Mux: Subtitles, Captions, WebVTT, HLS, and those magic flags](https://mux.com/blog/subtitles-captions-webvtt-hls-and-those-magic-flags/)

  Suggests they don't support CEA608/708 :(

* [libcaption](https://github.com/szatmary/libcaption) library and tools for handling CEA-608/708 streams in FLV

  Author wrote it while at Twitch, now works for Mux?

* [47 CFR 15.119 - Closed caption decoder requirements for analog television receivers](https://www.govinfo.gov/content/pkg/CFR-2007-title47-vol1/pdf/CFR-2007-title47-vol1-sec15-119.pdf)

  Describes CEA-608 caption format.

## encode and stream loops

Encode video as h264 baseline in FLV container, preserving CEA608/708 captions (if present):

```sh
ffmpeg -i source.ts -f flv -vcodec h264 -profile:v baseline output.flv
```

Using [Mux's standard input params](https://docs.mux.com/guides/video/minimize-processing-time#how-to-create-standard-input-ffmpeg):

```sh
ffmpeg -i source.ts -f flv \
    -vcodec h264 -profile:v high -b:v 7000k -pix_fmt yuv420p \
    -acodec aac -ac 2 output.flv
```

* assumes maximum 1080p input with square pixels, add `-vf "scale=w=min(iw\,1920):h=-2"` to scale.
* Video: H.264 with High profile, 8-bit 4:2:0 colour space @ 7mbit/s
* Audio: AAC stereo
* Retains CEA-608/708 subtitles from original stream (H.264 is a compatible container)

Stream a pre-recorded FLV to Mux on a loop without transcoding:

```sh
ffmpeg -stream_loop -1 -re -i input.flv \
    -c copy -f flv "rtmps://global-live.mux.com:443/app/${STREAM_KEY}"
```

* `-stream_loop -1`: repeat stream forever
* `-re`: read input at native framerate (otherwise we'll stream too fast)
* `-i input.flv`: input file
* `-c copy`: don't transcode
* `-f flv`: output as flv container

## ffprobe outputs

FLV with H.264 video and embedded CEA-608 captions:

```
Input #0, flv, from '':
  Metadata:
    encoder         : Lavf58.29.100
  Duration: 00:01:00.03, start: 0.000000, bitrate: 1542 kb/s
    Stream #0:0: Video: h264 (Constrained Baseline), yuv420p(progressive), 1280x720 [SAR 1:1 DAR 16:9], Closed Captions, 59.94 fps, 59.94 tbr, 1k tbn, 119.88 tbc
    Stream #0:1: Audio: mp3, 48000 Hz, stereo, fltp, 128 kb/s
```

Mux.com stream, source had CEA-608 captions which were stripped:

```
  Duration: N/A, start: 174.004667, bitrate: N/A
  Program 0
    Metadata:
      variant_bitrate : 2516370
    Stream #0:0: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 1280x720, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 2516370
    Stream #0:1: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 2516370
  Program 1
    Metadata:
      variant_bitrate : 1640580
    Stream #0:2: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 960x540, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 1640580
    Stream #0:3: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 1640580
  Program 2
    Metadata:
      variant_bitrate : 994068
    Stream #0:4: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 640x360, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 994068
    Stream #0:5: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 994068
  Program 3
    Metadata:
      variant_bitrate : 697078
    Stream #0:6: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 480x270, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 697078
    Stream #0:7: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 697078
```

Using Mux's recommended parameters:

```
Input #0, flv, from '':
  Metadata:
    encoder         : Lavf58.29.100
  Duration: 00:01:00.03, start: 0.000000, bitrate: 7074 kb/s
    Stream #0:0: Video: h264 (High), yuv420p(progressive), 1280x720 [SAR 1:1 DAR 16:9], Closed Captions, 7000 kb/s, 59.94 fps, 59.94 tbr, 1k tbn, 119.88 tbc
    Stream #0:1: Audio: aac (LC), 48000 Hz, stereo, fltp, 128 kb/s
```

Same output :(

```
  Duration: N/A, start: 142.011000, bitrate: N/A
  Program 0
    Metadata:
      variant_bitrate : 2516370
    Stream #0:0: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 1280x720, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 2516370
    Stream #0:1: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 2516370
  Program 1
    Metadata:
      variant_bitrate : 1640580
    Stream #0:2: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 960x540, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 1640580
    Stream #0:3: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 1640580
  Program 2
    Metadata:
      variant_bitrate : 994068
    Stream #0:4: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 640x360, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 994068
    Stream #0:5: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 994068
  Program 3
    Metadata:
      variant_bitrate : 697078
    Stream #0:6: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 480x270, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 697078
    Stream #0:7: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 697078
```

Asset (recorded live stream) is also missing captions:

```
  Duration: 00:12:32.47, start: 10.006000, bitrate: 0 kb/s
  Program 0
    Metadata:
      variant_bitrate : 2516370
    Stream #0:0: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 1280x720, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 2516370
    Stream #0:1: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 2516370
  Program 1
    Metadata:
      variant_bitrate : 1640580
    Stream #0:2: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 960x540, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 1640580
    Stream #0:3: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 1640580
  Program 2
    Metadata:
      variant_bitrate : 994068
    Stream #0:4: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 640x360, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 994068
    Stream #0:5: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 994068
  Program 3
    Metadata:
      variant_bitrate : 697078
    Stream #0:6: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p, 480x270, 59.94 fps, 59.94 tbr, 90k tbn, 1411200000.00 tbc
    Metadata:
      variant_bitrate : 697078
    Stream #0:7: Audio: aac (LC) ([15][0][0][0] / 0x000F), 48000 Hz, stereo, fltp
    Metadata:
      variant_bitrate : 697078
```