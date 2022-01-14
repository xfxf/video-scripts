# subtitles streaming notes

* Most online video streaming platforms accept CTA-608 or CTA-708 captions, and then transcode it to WebVTT or TTML for final rendering.

  CTA-608/708 are the captioning standards for US broadcast television.

  They **do not** accept other caption formats, even WebVTT, even though they transcode to WebVTT at the end!

* CTA-608 supports up to 4 caption channels:

  * CC1: primary, synchronous caption channel. Field 1 when interlaced. Most online video providers _only_ support this channel, and nothing else.
  * CC3: secondary, synchnorous caption channel. Field 2 when interlaced.
  * CC2, CC4: special, non-synchronous caption channels. This is sometimes used to show the name of the current program.

  There's also XDS which is a way to send structured program guide data, and to describe which language each caption track is for. In a US broadcast, CC1 is normally English, and CC3 is normally Spanish. _Generally unsupported for online streaming._

  The standard specifies how to encode on Line 21 (NTSC vertical blanking interval); but can also be carried in digital video (described later).

  CTA-608 has a limited character set, and limited style controls (no fonts).

* CTA-708 supports up to 16 caption _services_: S1 - S16.

  CTA-708 supports Unicode, and has more text and formatting styles.

  * Most video encoded with broadcast tools with CTA-708 captions also carries a CTA-608 caption track for compatibility reasons.
  
    eg: VLC doesn't play from the CTA-708 track _unless you explicitly configure it_:
    
    Settings -> Advanced -> Input/Codecs -> Track settings -> Preferred Closed Captions decoder: choose "EIA/CEA-608" (default) or "CEA-708"
  
* CTA-608/708 are carried inside of the video frame bitstream:

  * Both types of captions are carried in a DTVCC transport layer, specified in CTA-708-E Section 4.

  * This transport layer is carried inside ATSC A/53 Part 4 `atsc_user_data()` field (`GA94`).

  * In H.264 (and possibly H.265?) this `atsc_user_data()` field is tacked onto an ITU-T T.35 user data SEI payload:

    * Country: United Status (0xB5) (this is used regardless of the country of origin of the content)
    * Provider code: ATSC (0x0031)

    It's a little different for MPEG-2 and SDI, but we're mostly working with H.264 so we'll stick to this.
  
  * Per Rec. ITU-T H.264 §7.4.1.2.3 (version 14), SEI NALs must be:

    * _After_ the AUD, SPS and PPS NALs
    * _Before_ the first VCL NAL of a primary coded picture

    Practically speaking, this means the SEI NAL appears in any frame, but needs to be before any picture data.

  You don't actually need to transcode H.264 in order to insert captions -- you can "simply" rewrite the video frame bitstream to add in captions. This is what things like [Falcon](https://eegent.com/products/YH7XPZZU35A2OYN6/icap-falcon) do.

  _If this sounds horrificly complicated and easy to screw up, that's because it is._ See [my implementation attempt for gstreamer](https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/1178).

* For content, CTA-608/708 present a TTY-like interface which lets you put text on the screen, in a few different ways:

  * _Pop-on:_ incoming text is pushed to an off-screen buffer, and then swapped on cue.

    This is used for pre-recorded content - it sends text _before_ it is spoken, then swapped when it should be shown.

  * _Roll-up:_ incoming text is displayed immediately.  "Roll-up" is what happens on a carriage return:

    * The top line is deleted.
    * All other lines are moved up by 1 line (up to 4 lines), with a nice smooth animation as the new text comes in.
    * New text is added on the bottom line.
    
    This is used for live content.

  * _Paint-on:_ incoming text is displayed immediately. There is no fancy stuff, you are drawing on a character buffer.

    I think this is intended for some Teletext-like information service?

* _I mentioned transcoding!_ YouTube and Mux turn this into TTML and WebVTT respectively.

  But you say -- "hang on, those require discrete cues, and you can't just _modify_ parts of those cues after the fact!"

  They work around this -- they take snapshot of the caption display buffer on each frame, and create a series of cues that describe the _complete_ caption buffer state at any point in time.

  When you are streaming HLS, you are sending small chunks of video and audio, each of them a few seconds long. The same happens with subtitle data.

  If the caption display buffer doesn't change, then it just repeats the same caption again for a few more seconds.

  There are some limitations:

  * Colours and font styles are unsupported. WebVTT could support this, but Mux doesn't implement it.
  * On WebVTT, there is no roll-up animation.

* Also, _your captions can time travel_! When you have your captions inserted at the _end_ of your pipeline, you can delay audio and video until the captions are ready:

  * Incoming video and audio goes into a 5 second ring-buffer.
  * Captioner writes out the words in the buffer (a few seconds late)
  * The captioner's inputs are encoded into the video bitstream, at an _earlier_ point in the ring buffer (so it appears at the correct time). Because this doesn't need transcoding, it's very fast!
  * The final muxed output is then delivered for broadcast to viewers.

  Caption users aren't ever waiting at that point, because all viewers see the program after the ring buffer.

Useful links:

* [Mux: Subtitles, Captions, WebVTT, HLS, and those magic flags](https://mux.com/blog/subtitles-captions-webvtt-hls-and-those-magic-flags/) ~~Suggests they don't support CTA 608/708 :(~~

  **Update (Nov 2021):** [Mux now supports live 608 captions](#mux-attempt-2-november-2021). 

* [libcaption](https://github.com/szatmary/libcaption) library and tools for handling CTA-608/708 streams in FLV

  Author wrote it while at Twitch, now works for Mux?

* [47 CFR 15.119 - Closed caption decoder requirements for analog television receivers](https://www.govinfo.gov/content/pkg/CFR-2007-title47-vol1/pdf/CFR-2007-title47-vol1-sec15-119.pdf)

  Describes CTA-608 caption format.

* [ANSI/CTA-708-E R-2018](https://shop.cta.tech/products/digital-television-dtv-closed-captioning). While this is published in the CTA webshop, it costs $0.

* Wikipedia describes formats:

  * https://en.wikipedia.org/wiki/EIA-608 (still present)
  * https://en.wikipedia.org/wiki/CEA-708 (errors have been reported in the format description, _content removed September 2021_)

* [ATSC A/53 Part 4](https://www.atsc.org/atsc-documents/a53-atsc-digital-television-standard/) describes `ATSC_user_data` aka (`GA94`), which is a user data field inside the video bitstream where the captions are stored.

* [Rec. ITU-T H.264](https://www.itu.int/rec/T-REC-H.264)

* [Caption Inspector](#caption-inspector), notes below.

## Streamtext.net

* `streamtext_client.py`: reverse engineered client for StreamText, pulls the live feed and displays on CLI
* `streamtext_monitor.py`: export StreamText metrics for Prometheus, so we can see if we're still getting data
* `streamtext_to_cea608gdp.py`: exports StreamText as gstreamer `ttjson` over GDP (gstreamer data protocol), for use with the `tttocea608` element

## OBS

OBS supports CTA-708 output, but only in three ways:

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

* uses libcaption, uses 608 captions
* only supports complete caption updates, no backspace support
* currently going through major rewrite, not accepting patches on 4.x, master branch (5.x) is incomplete
* [obs-websockets-streamtext-captions](https://github.com/EddieCameron/obs-websocket-streamtext-captions): provides bridge from Streamtext.net into WebSockets-OBS, but only supports complete subs, no backspace

Decklink SDI:

* requires SDI source with CTA-708 CC feed
* decklink-captions patch added support for CTA-708 sources, shows how it works inside of OBS: https://github.com/obsproject/obs-studio/pull/2857/files
* unclear how "mixing" multiple CTA-708 sources works

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
* Retains CTA-608/708 subtitles from original stream (H.264 is a compatible container)

## Mux

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

### Mux, attempt 2 (November 2021)

[Mux recently announced support for captioning](https://mux.com/blog/support-for-captions-in-live-videos-now-available-crowd-cheers-louder/) (Oct 2021). Lets try this out!

```json
{
  "playback_policy" : [
    "public"
  ],
  "embedded_subtitles" : [
    {
      "name": "English CC",
      "passthrough": "English closed captions",
      "language_code": "en",
      "language_channel": "cc1"
    }
  ],
  "new_asset_settings": {
    "playback_policy": ["public"],
    "master_access": "temporary"
  },
  "reduced_latency": true
}
```

Testing players:

* hlsjs: just works, but need to manually turn on CC in the UI

  Add `?default_subtitles_lang=en` to the M3U8 URL to enable by default.

* VLC: no subtitle track!

Notes about their support:

* Mux renders the captions into WebVTT format with discrete cues.

* 608 with pop-on captions (like pre-recorded content):

  * Using H.264 High profile and a 60sec loop has breaks in the loop... Mux stalls out for about 12 seconds.
  * Using Baseline profile and a 120sec loop works OK, even when the captions start 30 seconds into the video.

* 608 with roll-up captions:

  * Mux doesn't work with our libcaption fork's roll-up (it disconnects after about 20 seconds).
  * Mux works with gstreamer generated captions (tttocea608 + streamtext_to_cea608gdp).
  * Mux will convert roll-ups into discrete cues.
  
    By comparison, YouTube converts roll-ups into an internal format which does the line-feed animation nicely.

    AU Teletext live TV captions doesn't do roll-up line-feed animations either, so they won't notice it's missing. US CC live TV captions does roll-ups, US viewers might notice it.

* The A/53 (608) track is _removed_ from the video track on output.  There is no pass-through.

  We don't control how any of the 608 is rendered, we are essentially beholden to how good or bad that is (as with YouTube).

* [Set up "master access" for asset recordings](https://docs.mux.com/guides/video/download-your-videos#download-for-editing-and-post-production): `new_asset_settings.master_access = true`.

  Mux keeps a copy of the original stream, including any 608/708 captions.

Streamtext to gstreamer pipeline with roll-up:

```sh
gstgit-launch cccombiner name=ccc schedule=false ! h264parse insert-cc=a53 ! mp4mux name=muxer ! filesink location=./gst-608ball-streamtext-live.mp4 \
  filesrc location=./balltime-avc-au-baseline.mp4 ! qtdemux name=q ! queue ! ccc. \
  tcpserversrc port=3000 ! gdpdepay ! tttocea608 ! closedcaption/x-cea-608 ! ccconverter ! closedcaption/x-cea-708,format=cc_data ! ccc.caption \
  q.audio_0 ! queue ! muxer.

python3 streamtext_to_cea608gdp.py IHaveADream -l en

ffmpeg -stream_loop -1 -re -i gst-608ball-streamtext-live.mp4 -c copy -f flv "rtmps://global-live.mux.com:443/app/${STREAM_KEY}"
```

Mux converts the CTA-608 caption track into WebVTT.  For roll-up, these are converted to pop-on cues:

Streamtext output / GStreamer input:

```
>> {"lines": [{"chunks": [{"text": "open the doors of", "style": "White", "underline": false}], "carriage_return": false}], "mode": "RollUp3"}
>> {"lines": [{"chunks": [{"text": "opportunity to", "style": "White", "underline": false}], "carriage_return": false}], "mode": "RollUp3"}
```

GStreamer output / Mux input (debug output from Caption Inspector):

```
00:01:11,133  F1:6E20  F1:F468  F1:E520  F1:94AD  F1:9426    Ch1: "n "  Ch1: "th"  Ch1: "e "  Ch1 {CR}   Ch1 {RU3}    Chan-1:  "n"  " "  Chan-1:  "t"  "h"  Chan-1:  "e"  " "  _Carriage Return_  Roll Up -  3 Rows  
              F1:94D0  F1:64EF  F1:EFF2  F1:7320  F1:EFE6    Ch1 - PAC  Ch1: "do"  Ch1: "or"  Ch1: "s "  Ch1: "of"    Row:14  Column:00  Chan-1:  "d"  "o"  Chan-1:  "o"  "r"  Chan-1:  "s"  " "  Chan-1:  "o"  "f"  
TEXT: Ch1 - "n the doors of" 

...

00:01:11,566  
TEXT: Ch1 - " o" 

00:01:11,600  
TEXT: Ch1 - "pp" 

00:01:11,633  F1:EFF2  F1:F475  F1:6EE9  F1:F479  F1:20F4    Ch1: "or"  Ch1: "tu"  Ch1: "ni"  Ch1: "ty"  Ch1: " t"    Chan-1:  "o"  "r"  Chan-1:  "t"  "u"  Chan-1:  "n"  "i"  Chan-1:  "t"  "y"  Chan-1:  " "  "t"  
TEXT: Ch1 - "ortunity to" 
```

Mux output:

```webvtt
WEBVTT
X-TIMESTAMP-MAP=LOCAL:00:00:00.000,MPEGTS:900000

00:35:48.000 --> 00:35:48.242 position:10.00% size:80.00% align:start
sunlit path of racial justice.
Now is the time to open the
doors of

00:35:48.242 --> 00:35:48.275 position:10.00% size:80.00% align:start
sunlit path of racial justice.
Now is the time to open the
doors of o

00:35:48.275 --> 00:35:48.309 position:10.00% size:80.00% align:start
sunlit path of racial justice.
Now is the time to open the
doors of opp

00:35:48.309 --> 00:35:48.709 position:10.00% size:80.00% align:start
sunlit path of racial justice.
Now is the time to open the
doors of opportunity to
```

Mux playlist fragment sample:

```
#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="sub1",CHARACTERISTICS="public.accessibility.transcribes-spoken-dialog,public.accessibility.describes-music-and-sound",NAME="English CC",AUTOSELECT=YES,DEFAULT=NO,FORCED=NO,LANGUAGE="en-US",URI="https://manifest-gce-us-east4-production.fastly.mux.com/123123/subtitles.m3u8?expires=123123&signature=123123=="
```

The playlist [declares that we're sending SDH](https://datatracker.ietf.org/doc/html/rfc8216#section-4.3.4.1) (transcribing all audio cues, not just dialogue)... but we actually haven't declared this on the Mux side.

## muxing our own CTA-608 caption track

TODO: Need some bug fixes in libcaption:

* https://github.com/szatmary/libcaption/pull/49
* party.c "party dudes" don't work on YouTube

CTA-608 frame is 32 columns x 15 rows. Need to adjust the line wrapping on subs - Subtitle Edit can do this (break/split long lines). Also tried using `fold`, but this **didn't** work well due to long cues:

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

* libcaption only does CTA-608 captions (which are very limited), despite structures saying otherwise
* large cues may cause it to encode bad data, would need to make much shorter cues and do windowing properly ?
* CTA-608 `caption_block_count`/`cc_count` size is 5 bits, so can have up to 31 blocks per GOP. 4 blocks are "reserved" at the start and end, and each block can store 2 characters max => 27-54 characters

**Note:** Caption Inspector is very fussy about its inputs, and will barf on homebrew files:

* if you have a frame with a number of DTVCC packets that is **not** a multiple of 5, it doesn't give you much debug info
* if you have an inappropriate number of DTVCC packets for the framerate, it will complain a lot
* there are some conditions in which you can crash it...

I have reported some of those issues upstream, when I figured out how I broke it.

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

The CTA-608 protocol is a bit like a terminal; we need a `terminfo` to make it do what we want. ;)

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

**Please don't use my libcaption fork.**  This was a bunch of experiments, and I'm moving on to gstreamer instead.

### gstreamer

I should have looked at this sooner. :)

608 related plugins: https://gitlab.freedesktop.org/gstreamer/gst-plugins-rs/-/tree/master/video/closedcaption/src

Notes:

* It looks like this can do a lot of stuff with 608, not so much with 708.
* Includes support for muxing and demuxing `.scc` and `.mcc`, which allows passing 608 and 708 streams.
* Largely written in Rust.
* Uses libcaption for some things, but a cut down version because gstreamer can do a lot of the mpeg stuff itself. It would be nice to replace libcaption with a Rust implementation.

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

Debug:

```
gstgit-launch -v --gst-debug=ccconverter:7 \
  cccombiner name=ccc ! cea608overlay ! x264enc pass=quant ! mp4mux name=muxer ! filesink location=/tmp/608.mp4 \
  videotestsrc num-buffers=600 ! video/x-raw,width=640,height=480 ! queue ! ccc. \
  filesrc location=/tmp/pep/pep458-sub.mcc ! mccparse ! queue ! ccconverter ! closedcaption/x-cea-708,format=cc_data ! ccc.caption
```

Appears to not only write the first cc_data bytepair, not the second?

```
# Input
00:00:02,000  F1:942C  F1:9440  X1:0000  X1:0000  X1:0000    Ch1 {EDM}  Ch1 - PAC  _________  _________  _________    EraseDisplayedMem  _Row:14 -  White_  _________________  _________________  _________________  

00:00:02,033  F1:9425  F1:94AD  X1:0000  X1:0000  X1:0000    Ch1 {RU2}  Ch1 {CR}   _________  _________  _________    Roll Up -  2 Rows  _Carriage Return_  _________________  _________________  _________________  

00:00:02,200  F1:9440  F1:5468  X1:0000  X1:0000  X1:0000    Ch1 - PAC  Ch1: "Th"  _________  _________  _________    _Row:14 -  White_  Chan-1:  "T"  "h"  _________________  _________________  _________________  
TEXT: Ch1 - "Th" 

00:00:02,333  F1:E973  F1:2080  X1:0000  X1:0000  X1:0000    Ch1: "is"  Ch1 - " "  _________  _________  _________    Chan-1:  "i"  "s"  Channel - 1:  " "  _________________  _________________  _________________  
TEXT: Ch1 - "is " 

00:00:02,000 - {EDM} {R14:White}
00:00:02,033 - {RU2} {CR} {R14:White} "This PEP describes changes to "

# Output
00:00:01,866 - {EDM}
00:00:01,900 - {RU2} {R14:White} "isPEderis chgeto"
```

Debug output:

```
0:00:00.026507900 10466 0x564e3c8edb00 DEBUG            ccconverter gstccconverter.c:2155:gst_cc_converter_transform:<ccconverter0> Converting buffer: 0x7f6c5800bc60, pts 0:00:02.000000000, dts 99:99:99.999999999, dur 0:00:00.033333334, size 28, offset none, offset_end none, flags 0x0 from 4 to 3
0:00:00.026532700 10466 0x564e3c8edb00 LOG              ccconverter gstccconverter.c:645:compact_cc_data: compacted cc_data from 15 to 6
0:00:00.026559900 10466 0x564e3c8edb00 TRACE            ccconverter gstccconverter.c:676:cc_data_extract_cea608: 0xfc 0x94 0x2c, valid: 1, type: 0b00
0:00:00.026584100 10466 0x564e3c8edb00 TRACE            ccconverter gstccconverter.c:676:cc_data_extract_cea608: 0xfc 0x94 0x40, valid: 1, type: 0b00
0:00:00.026608000 10466 0x564e3c8edb00 LOG              ccconverter gstccconverter.c:714:cc_data_extract_cea608: Extracted cea608-1 of length 4 and cea608-2 of length 0
0:00:00.026632600 10466 0x564e3c8edb00 DEBUG            ccconverter gstccconverter.c:1029:fit_and_scale_cc_data:<ccconverter0> write out packet with lengths ccp:0, cea608-1:4, cea608-2:0
0:00:00.026657100 10466 0x564e3c8edb00 LOG              ccconverter gstccconverter.c:814:combine_cc_data: writing 2 cea608-1 fields and 0 cea608-2 fields
0:00:00.026683700 10466 0x564e3c8edb00 DEBUG            ccconverter gstccconverter.c:2273:gst_cc_converter_transform:<ccconverter0> Converted to buffer: 0x7f6c500047e0, pts 0:00:02.000000000, dts 99:99:99.999999999, dur 0:00:00.033333334, size 6, offset none, offset_end none, flags 0x0
0:00:00.026756100 10466 0x564e3c8edb00 DEBUG            ccconverter gstccconverter.c:2155:gst_cc_converter_transform:<ccconverter0> Converting buffer: 0x7f6c5800ba20, pts 0:00:02.033333333, dts 99:99:99.999999999, dur 0:00:00.033333334, size 28, offset none, offset_end none, flags 0x0 from 4 to 3
0:00:00.026780900 10466 0x564e3c8edb00 LOG              ccconverter gstccconverter.c:645:compact_cc_data: compacted cc_data from 15 to 6
0:00:00.026808200 10466 0x564e3c8edb00 TRACE            ccconverter gstccconverter.c:676:cc_data_extract_cea608: 0xfc 0x94 0x25, valid: 1, type: 0b00
0:00:00.026841500 10466 0x564e3c8edb00 TRACE            ccconverter gstccconverter.c:676:cc_data_extract_cea608: 0xfc 0x94 0xad, valid: 1, type: 0b00
0:00:00.026848200 10466 0x564e3c8edb00 LOG              ccconverter gstccconverter.c:714:cc_data_extract_cea608: Extracted cea608-1 of length 4 and cea608-2 of length 0
0:00:00.026932800 10466 0x564e3c8edb00 DEBUG            ccconverter gstccconverter.c:1029:fit_and_scale_cc_data:<ccconverter0> write out packet with lengths ccp:0, cea608-1:4, cea608-2:0
0:00:00.026959200 10466 0x564e3c8edb00 LOG              ccconverter gstccconverter.c:814:combine_cc_data: writing 2 cea608-1 fields and 0 cea608-2 fields
0:00:00.026988100 10466 0x564e3c8edb00 DEBUG            ccconverter gstccconverter.c:2273:gst_cc_converter_transform:<ccconverter0> Converted to buffer: 0x7f6c5800b5a0, pts 0:00:02.033333333, dts 99:99:99.999999999, dur 0:00:00.033333334, size 6, offset none, offset_end none, flags 0x0
```

Looks like `cccombiner` sees both bytepairs, but only the first one makes it through.

`cc708overlay` requires a split CTA-708 stream (`cc_sink`), it can't handle `GstVideoCaptionMeta`.

Converting from SRT:

```sh
gstgit-launch -v \
  cccombiner name=ccc ! cea608overlay ! x264enc pass=quant ! mp4mux name=muxer ! filesink location=/tmp/608.mp4 \
  videotestsrc num-buffers=6000 pattern=ball ! video/x-raw,width=1280,height=720 ! queue ! ccc. \
  filesrc location=~/subtitle.srt ! subparse ! tttocea608  mode=pop-on ! closedcaption/x-cea-608,framerate=30/1 !  ccconverter ! closedcaption/x-cea-708,format=cc_data ! ccc.caption
```

This mostly works, doesn't handle some entity escaping properly, and using roll-up isn't the same as pop-up.  It only uses one cc_data pair per frame -- so it seems like gstreamer really doesn't like us two field-1 `cc_data` in a frame.

`tttocea608` requires a source with PTS (timing).  It can read in raw text a line at a time, or a newline-separated JSON based on [`struct Lines`](https://gitlab.freedesktop.org/gstreamer/gst-plugins-rs/-/blob/master/video/closedcaption/src/ttutils.rs#L81). Doing the timestamp matching with an interactive source will be interesting. Video encoder should be able to add timestamps on wall time.

`gdp.py` has an implementation of gStreamer Data Protocol, and some glue code code for reading from StreamText.  It does not support text edits -- `ttjson` doesn't support editing.

A complete-ish pipeline for that, with subs delivered as `ttjson` over `tcp:localhost:3000`:

```sh
gstgit-launch -v \
  cccombiner name=ccc schedule=false ! timecodestamper ! cea608overlay ! \
    timeoverlay time-mode=time-code ! x264enc pass=quant ! \
    mp4mux name=muxer filesink location=/tmp/608live.mp4 \
  videotestsrc num-buffers=600 pattern=ball ! video/x-raw,width=1280,height=720 ! queue ! ccc. \
  tcpserversrc port=3000 ! gdpdepay ! tttocea608 ! \
    closedcaption/x-cea-608 ! ccconverter ! \
    closedcaption/x-cea-708,format=cc_data ! ccc.caption
```

#### gstreamer transcode requirement

gstreamer has an underlying issue though - it requires transcoding to be able to mux captions, you can't just inject a SEI.

Started writing a patch: https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/1178

```sh
gstgit-launch -v \
  cccombiner name=ccc schedule=false ! h264parse insert-cc=a53 ! \
    mp4mux name=muxer ! filesink location=/tmp/608live.mp4 \
  filesrc location=./ball.mp4 ! qtdemux name=q ! queue ! ccc. \
  tcpserversrc port=3000 ! gdpdepay ! tttocea608 ! \
    closedcaption/x-cea-608 ! ccconverter ! \
    closedcaption/x-cea-708,format=cc_data ! ccc.caption \
  q.audio_0 ! queue ! muxer.
```

Can't put caption data on frame 0.  That does bad things.  May have an issue with SEI being part of the wrong frame? unsure.

`cccombiner schedule=false` is critical -- else all the captions get jumbled up (DTS order != PTS order).

#### misc tttocea608 issues

* `tttocea608` still likes having real durations on `RollUp` captions -- this allows it to smear output across multiple frames.  Using `duration=1` (nanosecond) _works_, it's just not that nice.

* `tttocea608` [PopOn is always late](https://gitlab.freedesktop.org/gstreamer/gst-plugins-rs/-/issues/172), it doesn't start processing a cue until **at** PTS.

### test video

Pinwheel with timecode and audio pips:

```sh
gstgit-launch mp4mux name=mp4 ! filesink location=./pinwheel-audio.mp4 \
  videotestsrc num-buffers=3600 pattern=pinwheel ! video/x-raw,width=1280,height=720,framerate=30/1 ! \
    timecodestamper ! timeoverlay time-mode=time-code ! x264enc pass=quant ! video/x-h264,profile=baseline ! mp4. \
  audiotestsrc do-timestamp=true wave=ticks num-buffers=5200 ! audioconvert ! avenc_aac ! mp4.audio_0
```

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

### TTML

* https://muygs2x2vhb2pjk6g160f1s8-wpengine.netdna-ssl.com/wp-content/uploads/2021/04/A343-2018-Captions-and-Subtitles.pdf
* https://muygs2x2vhb2pjk6g160f1s8-wpengine.netdna-ssl.com/wp-content/uploads/2021/09/A343-2018-Captions-and-Subtitles-with-Amend-1-2.pdf

Annex A is interesting.

* https://bbc.github.io/ttml-in-subtitle-flows-csun-presentation/

iOS doesn't support TTML?

* https://docs.edgecast.com/video/Content/Setup/Captions-Subtitles.htm
* https://github.com/google/shaka-player/issues/986
* HLS.js may support it in an IMSC blob? or with a sideloaded track.
  * https://github.com/video-dev/hls.js/pull/3016


#### Shaka

Shaka player does TTML?

https://storage.googleapis.com/shaka-demo-assets/angel-one/dash.mpd points at https://storage.googleapis.com/shaka-demo-assets/angel-one/text_en.mp4, it's doing byte range fetches for blobs on GCS.

Mediainfo says:

```
General
Complete name                            : text_en.mp4
Format                                   : MPEG-4
Format profile                           : Base Media
Codec ID                                 : isom (iso8/mp41/dash/cmfc)
File size                                : 5.14 KiB
Duration                                 : 1 min 4 s
Overall bit rate                         : 658 b/s
Encoded date                             : UTC 2020-02-13 01:45:36
Tagged date                              : UTC 2020-02-13 01:45:36

Text
ID                                       : 1
Format                                   : wvtt
Codec ID                                 : wvtt
Duration                                 : 1 min 4 s
Bit rate                                 : 279 b/s
Stream size                              : 2.18 KiB (42%)
Language                                 : English
Forced                                   : No
Encoded date                             : UTC 2020-02-13 01:45:36
Tagged date                              : UTC 2020-02-13 01:45:36
```

* [DASH Source Simulator uses incorrectly formed H.264](https://github.com/Dash-Industry-Forum/dash-live-source-simulator/issues/99), which then [got adopted by a bunch of web players](https://github.com/google/shaka-player/issues/3715)
