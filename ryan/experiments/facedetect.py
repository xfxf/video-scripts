#!/usr/bin/env python3
"""
Face detection via gstreamer experiment.
The functions below to parse the GstMessage are super hacky, but they appear to work for facedetect.
"""

import re
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

GObject.threads_init()
Gst.init([])


def parse_gstvaluelist_substructure(structure):
    """
    Breaks up a gstvaluelist structure into seperate chunks (and parses them), with unique keys.
    """

    structure_escaped = structure.replace('\\', '')
    strings = [item.groupdict() for item in re.finditer(r'"(?P<substructure>[^\;;]*;)"', structure_escaped)]

    data = {}
    for idx, string in enumerate(strings):
        data[idx] = parse_gstvaluelist_string(string['substructure'])
    return data

def parse_gstvaluelist_string(string):
    """
    Parses a gstreamer bus message.get_structure.to_string() and returns a nested dict of values.
    Alternative to message.get_structure().get_value('key') - currently results in "TypeError: unknown type GstValueList"

    Example input:
        facedetect, timestamp=(guint64)16540000000, stream-time=(guint64)16540000000, running-time=(guint64)15800000000, duration=(guint64)200000000, faces=(structure){ "face\,\ x\=\(uint\)93\,\ y\=\(uint\)71\,\ width\=\(uint\)219\,\ height\=\(uint\)199\;", "face\,\ x\=\(uint\)411\,\ y\=\(uint\)166\,\ width\=\(uint\)189\,\ height\=\(uint\)171\;" };
    """

    subitems = re.finditer(r'(?P<key>[a-z0-9-]*)=\(structure\){(?P<structure>.*)};', string)
    subdata = [subitem.groupdict() for subitem in subitems]
    subdata_dict = {item['key']: parse_gstvaluelist_substructure(item['structure']) for item in subdata}

    items = re.finditer(r'(?P<key>[a-z-]*)=\((?P<type>[a-z0-9]*)\)(?P<value>[a-zA-Z0-9-]*)(, |;|\n)', string)
    data = [item.groupdict() for item in items]
    data_dict = {item['key']: cast_value(item['value'], item['type']) for item in data}

    data_dict.update(subdata_dict)
    return data_dict

def cast_value(value, to_type):
    """
    Hacky casting of specified type back to native Python type
    """
    if to_type == 'guint64' or 'uint':
        return int(value)
    elif to_type == 'timestamp':
        return int(value)  # consider converting to native type
    else:
        return value


class FaceDetect(object):

    def __init__(self):
        #PROFILE = 'haarcascade_mcs_upperbody.xml'
        #PROFILE = 'haarcascade_profileface.xml'
        PROFILE = 'haarcascade_frontalface_default.xml'
        #PROFILE = 'haarcascade_frontalface_alt2.xml'  # alt2, alt_tree
        #PROFILE = 'haarcascade_mcs_eyepair_small.xml'  # small

        #SOURCE = 'filesrc location=test.ts'
        SOURCE = 'v4l2src device=/dev/video0'

        WIDTH = 640  # int(1280/2)
        HEIGHT = 480  # int(720/2)
        FPS = 5

        pipe = """{} ! decodebin ! videorate ! videoscale ! videoconvert ! video/x-raw,width={},height={},framerate={}/1 ! facedetect display=true profile=/usr/share/opencv/haarcascades/{}  ! videoconvert ! ximagesink""".format(SOURCE, WIDTH, HEIGHT, FPS, PROFILE)

        self.pipeline = Gst.parse_launch(pipe)

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message::element", self.bus_message)

        self.pipeline.set_state(Gst.State.PLAYING)

    def bus_message(self, bus, message):
        st = message.get_structure()
        if st.get_name() == "facedetect":
            msg_contents = parse_gstvaluelist_string(st.to_string())
            if msg_contents and msg_contents.get('faces'):
                for faceno, face in msg_contents.get('faces').items():
                    print("Face %d found at %d,%d with dimensions %dx%d" % (faceno, face["x"], face["y"], face["width"], face["height"]))
        else:
            print(st.get_name())


if __name__ == "__main__":
    f = FaceDetect()
    mainloop = GObject.MainLoop()
    mainloop.run()

