# subtitles streaming notes

* [Mux: Subtitles, Captions, WebVTT, HLS, and those magic flags](https://mux.com/blog/subtitles-captions-webvtt-hls-and-those-magic-flags/)

  Suggests they don't support CEA608/708 :(

* [libcaption](https://github.com/szatmary/libcaption) library and tools for handling CEA-608/708 streams in FLV

  Author wrote it while at Twitch, now works for Mux?

* [47 CFR 15.119 - Closed caption decoder requirements for analog television receivers](https://www.govinfo.gov/content/pkg/CFR-2007-title47-vol1/pdf/CFR-2007-title47-vol1-sec15-119.pdf)

  Describes CEA-608 caption format.

* Wikipedia describes formats:

  * https://en.wikipedia.org/wiki/EIA-608
  * https://en.wikipedia.org/wiki/CEA-708

## Streamtext.net

* `streamtext_client.py`: reverse engineered client for StreamText, pulls the live feed and displays on CLI
* `streamtext_monitor.py`: uses our StreamText client library to export metrics for Prometheus, so we can see if we're still getting data

## OBS

OBS supports CEA-708 output, but only in three ways:

* In-built speech-to-text recognizer
* API call which injects subtitles
* Decklink SDI capture passthrough

Investigated adding support for subtitle pass-through for OBS VLC source:

* vlc-source uses [libvlc memory buffer API to get a decoded video and audio stream](https://code.videolan.org/videolan/vlc/-/blob/master/modules/stream_out/smem.c)
* libvlc doesn't appear to give any special access to the subtitle track
* we can only burn-in subtitles on to the video stream
* may be a way to use `#sout` to get a copy of the caption feed, haven't figured this out yet.
* there is a memfile interface, [but it appears to be read-only](https://videolan.videolan.me/vlc/group__libvlc__media.html#gabeece3802e4b17a655e45c4ff4a2bbda).

API call via OBS-WebSockets:

* only supports complete caption updates, no backspace support
* currently going through major rewrite, not accepting patches on 4.x, master branch (5.x) is incomplete
* [obs-websockets-streamtext-captions](https://github.com/EddieCameron/obs-websocket-streamtext-captions): provides bridge from Streamtext.net into WebSockets-OBS, but only supports complete subs, no backspace

Decklink SDI:

* requires SDI source with CEA-708 CC feed
* decklink-captions patch added support for CEA-708 sources, shows how it works inside of OBS: https://github.com/obsproject/obs-studio/pull/2857/files
* unclear how "mixing" multiple CEA-708 sources works

## ffmpeg

### encode and stream loops

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

### ffprobe outputs

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

### muxing our own CEA-608 caption track

TODO: Need some bug fixes in libcaption:

* https://github.com/szatmary/libcaption/pull/49
* party.c "party dudes" don't work on YouTube

CEA-608 frame is 32 columns x 15 rows. Need to adjust the line wrapping on subs - Subtitle Edit can do this (break/split long lines). Also tried using `fold`, but this **didn't** work well due to long cues:

```sh
# bad!
fold -sw 32 source.srt > output.srt
```

Muxing the file:

```sh
./libcaption/examples/flv+srt input.flv input.srt output.flv
```

This will spew a lot of debug output, but should show every caption it found.  File should be playable in VLC, after enabling CC Track 1.

Can also debug a file with:

```sh
./libcaption/examples/flv2srt input.flv 2>&1 | less
```

This sends caption debug data to `stderr`, and an SRT version to `stdout`.

TODO: figure out what rate we can send captions, and maybe use scrolling as well. This may sort out YouTube and VLC issues with this (unwrapped source file):

```
   timestamp: 0.033000
   row: 03    col: 25    roll-up: 0
   00000000001111111111222222222233        00000000001111111111222222222233
   01234567890123456789012345678901        01234567890123456789012345678901
  ┌--------------------------------┐      ┌--------------------------------┐
00|>> Hello, everyone, welcome     |    00|                                |
01|back. Up next, we               |    01|                                |
02|have the wonderful Leigh        |    02|                                |
03|Brenecki, who attendees         |    03|                                |
04|                                |    04|                                |
05|                                |    05|                                |
06|                                |    06|                                |
07|                                |    07|                                |
08|                                |    08|                                |
09|                                |    09|                                |
10|                                |    10|                                |
11|                                |    11|                                |
12|                                |    12|                                |
13|                                |    13|                                |
14|                                |    14|                                |
  └--------------------------------┘      └--------------------------------┘
```

TODO: consider rewriting libcaption or find an alternative - there's lots of weird bugs, limits enforced in strange ways

* https://github.com/Dash-Industry-Forum/media-tools/tree/master/python/dash_tools
* https://github.com/GStreamer/gst-plugins-bad/blob/master/ext/closedcaption/gstcccombiner.c

### caption-inspector

https://github.com/Comcast/caption-inspector

**Very helpful** - I can see a few things:

* libcaption only does CEA-608 captions (which are very limited), despite structures saying otherwise
* large cues may cause it to encode bad data, would need to make much shorter cues and do windowing properly ?
* EIA-608 `caption_block_count`/`cc_count` size is 5 bits, so can have up to 31 blocks per GOP. 4 blocks are "reserved" at the start and end, and each block can store 2 characters max => 27-54 characters

Pre-recorded broadcast content normally sends a lot less data at once than `libcaption`: `libcaption` tries to push 65 blocks in a frame, whereas broadcast typically sends 1 block per frame (or 2 blocks per frame for dual 608+708).

At the start of the program, reset everything:

1. `EOC` `EOC` (end of caption)
2. `EDM` `EDM` (erase display memory)
3. `ENM` `ENM` (erase non-display memory)

Then for each cue, for pre-record content:

1. start as soon as the previous caption is on-screen
2. send `RCL` `RCL` (resume caption loading) `ENM` `ENM` (erase non-display memory) to start a new buffer for the next caption
3. write out the first line to be displayed
4. if there are more lines, send `RCL` `RCL` before each new line, then the line
5. wait for previous cue end time
6. send `EDM` `EDM` (erase display memory) to hide previous cue
7. wait for cue start time
8. send `EOC` `EOC` (end of caption) to show next cue

For live "type it out", use the `RDC` (resume direct captioning) command.

The CEA-608 protocol is a bit like a terminal; we need a `terminfo` to make it do what we want. ;)

### libcaption playground

My playground branch: https://github.com/micolous/libcaption/

Stuff I've implemented:

* Implemented "smearing" of 608 captions, make it a lot more like broadcast; this exposed an issue with timecodes being out of order which I've tried to work around.
* Added `flv+karaoke`, this acts a bit more like a stenographer, and types a word at a time and uses roll-up.
* Added support for 708 / DTVCC muxing and parsing, and support for roll-up.

Issues:

* [Caption Inspector has an off-by-one for pen and window styles](https://github.com/Comcast/caption-inspector/issues/14), causes these to be labelled wrong
* VLC requires opting in to parsing 708 captions, by default it'll only look at 608. Fix: Set `Input / Codecs` -> `Preferred Closed Captions decoder` to `CEA 708`.
* [VLC has an off-by-one as well](https://code.videolan.org/videolan/vlc/-/issues/26160), which causes incorrect rendering **and** out of array bounds access.
* [VLC also is very sensitive about where 708 captions start](https://code.videolan.org/videolan/vlc/-/issues/26159)

### gstreamer

I should have looked at this sooner. :)

608 related plugins: https://gitlab.freedesktop.org/gstreamer/gst-plugins-rs/-/tree/master/video/closedcaption/src

Notes:

* It looks like this can do a lot of stuff with 608, not so much with 708.
* Includes support for muxing and demuxing `.scc` and `.mcc`, which allows passing 608 and 708 streams.
* Largely written in Rust.
* Uses libcaption for some things, but a cut down version because gstreamer can do a lot of the mpeg stuff itself.

Lets see if I can get into a workable state :)

Useful component in `gst-launch-1.0` is `identity silent=false ! fakesink`, this spits out lots of nice events for us.

Need to get the 608 stream, this is in the H264 SEI.

https://gitlab.freedesktop.org/gstreamer/gst-plugins-bad/-/issues/822 suggests something like:

```
GST_PLUGIN_PATH="target/x86_64-unknown-linux-gnu/debug:${GST_PLUGIN_PATH}" \
  gst-launch-1.0 -v \
    cccombiner name=ccc ! cea608overlay ! x264enc pass=quant ! \
      matroskamux ! filesink location=/tmp/608.mkv \
    uridecodebin uri=file:///tmp/counting-captioned.mov name=u \
    u. ! queue ! closedcaption/x-cea-608 ! ccconverter ! \
      closedcaption/x-cea-608, format=raw ! ccc.caption \
    u. ! video/x-raw ! queue ! ccc.sink
```

But the original file from the bug (MOV) had an explicit 608 track, whereas our files have it in an SEI: so this pipeline just stalls out.

https://gitlab.freedesktop.org/gstreamer/gst-plugins-base/-/issues/553 suggests we don't get it from metas

https://gitlab.freedesktop.org/gstreamer/gst-plugins-base/-/issues/553#note_726123 has an MPEG-2 compatible pipeline, which isn't working for H264

```
gst-launch-1.0 -v filesrc location=./pep458-sub.mp4 ! qtdemux ! h264parse ! identity silent=false ! fakesink

/GstPipeline:pipeline0/GstIdentity:identity0: last-message = chain   ******* (identity0:sink) (1267 bytes, dts: 0:01:10.067000000, pts: 0:01:10.100000000, duration: 0:00:00.033333333, offset: 24447026, offset_end: -1, flags: 00002400 header delta-unit , meta: GstVideoCaptionMeta) 0x7f1d7c006000

```

This doesn't work, it just stalls out:

```
gst-launch-1.0 -v filesrc location=./pep458-sub.mp4 ! qtdemux ! h264parse ! avdec_h264 ! ccextractor name=cx ! queue ! fakesink  cx. ! queue ! ccconverter ! capsfilter caps=closedcaption/x-cea-608,format=raw ! sccenc ! fakesink
```

Maybe a better strategy here is to use gstreamer _exclusively_ for mux, not demux?

```
GST_PLUGIN_PATH="target/x86_64-unknown-linux-gnu/debug:${GST_PLUGIN_PATH}"   gst-launch-1.0 -v  cccombiner name=ccc ! x264enc ! mp4mux ! filesink location=/tmp/remux.mp4    uridecodebin uri=file:///home/michael/pep458.flv ! ccc.sink  filesrc location=/tmp/smeared/pep458-dtv.mcc ! mccparse ! ccc.caption
```

Self built bits:

```
GST_PLUGIN_PATH="$HOME/.local/gst/lib/x86_64-linux-gnu/gstreamer-1.0" LD_LIBRARY_PATH="$HOME/.local/gst/lib/x86_64-linux-gnu" ~/.local/gst/bin/gst-inspect-1.0

GST_PLUGIN_PATH="$HOME/.local/gst/lib/x86_64-linux-gnu/gstreamer-1.0" LD_LIBRARY_PATH="$HOME/.local/gst/lib/x86_64-linux-gnu" ~/.local/gst/bin/gst-launch-1.0

GST_PLUGIN_PATH="$HOME/.local/gst/lib/x86_64-linux-gnu/gstreamer-1.0" LD_LIBRARY_PATH="$HOME/.local/gst/lib/x86_64-linux-gnu" ~/.local/gst/bin/gst-launch-1.0 -v  filesrc location=./pep458-dtv.mp4 ! qtdemux ! h264parse ! avdec_h264 ! queue ! video/x-raw ! ccextractor name=cx ! fakesink   cx. ! queue ! capsfilter caps=closedcaption/x-cea-708,format=cc_data ! ccconverter ! mccenc ! fakesink

/GstPipeline:pipeline0/RsMccEnc:rsmccenc0.GstPad:sink: caps = closedcaption/x-cea-708, format=(string)cdp, framerate=(fraction)60/1
/GstPipeline:pipeline0/GstCCConverter:ccconverter0.GstPad:sink: caps = closedcaption/x-cea-708, format=(string)cc_data, framerate=(fraction)30/1
ERROR: from element /GstPipeline:pipeline0/RsMccEnc:rsmccenc0: The stream is in the wrong format.
/GstPipeline:pipeline0/GstCapsFilter:capsfilter0.GstPad:sink: caps = closedcaption/x-cea-708, format=(string)cc_data, framerate=(fraction)30/1
Additional debug info:
video/closedcaption/src/mcc_enc/imp.rs(276): gstrsclosedcaption::mcc_enc::imp (): /GstPipeline:pipeline0/RsMccEnc:rsmccenc0:
Stream with timecodes on each buffer required
ERROR: pipeline doesn't want to preroll.
Setting pipeline to NULL ...
Freeing pipeline ...
```

Lets make things less messy:

```sh
alias gstgit-launch='GST_PLUGIN_PATH="$HOME/.local/gst/lib/x86_64-linux-gnu/gstreamer-1.0" LD_LIBRARY_PATH="$HOME/.local/gst/lib/x86_64-linux-gnu" ~/.local/gst/bin/gst-launch-1.0'
alias gstgit-inspect='GST_PLUGIN_PATH="$HOME/.local/gst/lib/x86_64-linux-gnu/gstreamer-1.0" LD_LIBRARY_PATH="$HOME/.local/gst/lib/x86_64-linux-gnu" ~/.local/gst/bin/gst-inspect-1.0'
```

Encodes captions, but output is messed up:

```sh
gstgit-launch -v \
  cccombiner name=ccc ! x264enc pass=quant ! mp4mux name=muxer ! filesink location=/tmp/608.mp4 \
  videotestsrc num-buffers=1800 ! video/x-raw,width=640,height=480 ! ccc. \
  filesrc location=/tmp/pep/pep458-sub.mcc ! mccparse ! ccconverter ! \
    closedcaption/x-cea-708,format=cc_data ! ccc.caption
```

This internal rendering looks correct:

```sh
gstgit-launch -v \
  cccombiner name=ccc ! cea608overlay ! x264enc pass=quant ! mp4mux name=muxer ! filesink location=/tmp/608.mp4 \
  videotestsrc num-buffers=600 ! video/x-raw,width=640,height=480 ! queue ! ccc. \
  filesrc location=/tmp/pep/pep458-sub.mcc ! mccparse ! queue ! ccconverter ! ccc.caption
```

gstreamer `x264enc` requires `caption_type == GST_VIDEO_CAPTION_TYPE_CEA708_RAW`, aka `closedcaption/x-cea-708,format=cc_data` to give us `GA94` payloads: https://gitlab.freedesktop.org/gstreamer/gstreamer/-/blob/main/subprojects/gst-plugins-ugly/ext/x264/gstx264enc.c#L2384

Forcing that format messes things up again, even on the `cea608overlay` render:

```sh
gstgit-launch -v \
  cccombiner name=ccc ! cea608overlay ! x264enc pass=quant ! mp4mux name=muxer ! filesink location=/tmp/608.mp4 \
  videotestsrc num-buffers=600 ! video/x-raw,width=640,height=480 ! queue ! ccc. \
  filesrc location=/tmp/pep/pep458-sub.mcc ! mccparse ! queue ! ccconverter ! closedcaption/x-cea-708,format=cc_data ! ccc.caption
```

At the moment, `ccconverter` looks like the culprit for badness.


### ffmpeg

ffmpeg can read and write SCC (Scenarist CC), and read MCC (MacCaption) 608 and 708 captions, as well as read captions embedded in a MPEG SEI (GA94 / ATSC A53 format). It can also render 608/708 as a hard sub:

```sh
ffmpeg -i source.flv \
  -vf subtitles=captions.mcc \
  -f mp4 -vcodec libx264 \
  -acodec copy output.flv
```

It can also preserve captions when transcoding.

However, it cannot mux 608/708 bytes into MPEG:

* https://trac.ffmpeg.org/ticket/1778#comment:10 (open ticket since 2015)
* https://lists.ffmpeg.org/pipermail/ffmpeg-user/2017-May/036251.html

There are some issues with some MPEG2 and MPEG4 encoders in ffmpeg preserving user data (used as a transport for 608/708).

### WebVTT

https://github.com/w3c/webvtt/issues/320
