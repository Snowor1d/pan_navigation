import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

Gst.init(None)

class RTSPMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **properties):
        super(RTSPMediaFactory, self).__init__(**properties)
        self.number_frames = 0
        #self.launch_string = 'v4l2src ! video/x-raw,width=640,height=480,framerate=30/1 ! videoconvert ! x264enc tune=zerolatency bitrate=800 speed-preset=superfast ! rtph264pay name=pay0 pt=96'
        self.launch_string = 'v4l2src ! video/x-raw,width=768,height=432,framerate=30/1 ! videoconvert ! x264enc tune=zerolatency bitrate=800 speed-preset=superfast ! rtph264pay name=pay0 pt=96'
	#self.launch_string = 'v4l2src ! video/x-raw,width=1280,height=720,framerate=30/1 ! videoconvert ! x264enc tune=zerolatency bitrate=800 speed-preset=superfast ! rtph264pay name=pay0 pt=96'

    def on_need_data(self, src, length):
        print("Generating frame")

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

class RTSPServer(GstRtspServer.RTSPServer):
    def __init__(self, **properties):
        super(RTSPServer, self).__init__(**properties)
        self.factory = RTSPMediaFactory()
        self.factory.set_shared(True)
        self.get_mount_points().add_factory("/test", self.factory)
        self.attach(None)

GObject.threads_init()
server = RTSPServer()

loop = GObject.MainLoop()
loop.run()
