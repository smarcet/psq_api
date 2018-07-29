import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib
import logging


class AbstractTranscoder:

    def __init__(self, input_file, output_file):
        self.pipeline = None
        self.bus = None
        self.pipeline_def = None
        self.input_file = input_file
        self.output_file = output_file
        self.logger = logging.getLogger('transcoder')

    def set_pipeline_def(self, pipeline_def):
        self.pipeline_def = pipeline_def.format(input_file = self.input_file, output_file= self.output_file)

    def apply(self):
        # initialize GStreamer
        Gst.init(None)

        self.logger.info("AbstractTranscoder - starting pipeline={pipeline_def}".format(pipeline_def=self.pipeline_def))
        self.pipeline = Gst.parse_launch(self.pipeline_def)

        self.pipeline.set_state(Gst.State.PLAYING)
        # wait until EOS or error
        self.bus = self.pipeline.get_bus()

        # wait until EOS or error
        msg = self.bus.timed_pop_filtered(
            Gst.CLOCK_TIME_NONE,
            Gst.MessageType.ERROR | Gst.MessageType.EOS
        )

        if msg.type == Gst.MessageType.ERROR:
            self.logger.info("AbstractTranscoder - Transcoding fatal error")
            res = msg.parse_error()
            self.logger.info(msg.src.name)
            self.logger.info(res[1])
        if msg.type == Gst.MessageType.EOS:
            self.logger.info("AbstractTranscoder - EOS Reached from element={element}".format(element=msg.src.name))

        # free resources
        self.logger.info("AbstractTranscoder - Execution ending ...")
        self.logger.info("AbstractTranscoder - Setting pipeline to PAUSED ...\n")
        res = self.pipeline.set_state(Gst.State.PAUSED)
        self.logger.info("AbstractTranscoder - Setting pipeline to READY ...\n")
        res = self.pipeline.set_state(Gst.State.READY)
        self.logger.info("AbstractTranscoder - Setting pipeline to NULL ...\n")
        res = self.pipeline.set_state(Gst.State.NULL)
        self.logger.info("AbstractTranscoder - Freeing pipeline ...\n")
        self.pipeline = None
        self.bus = None
        self.logger = None


class MKV2OGGTranscoder(AbstractTranscoder):

    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)
        self.set_pipeline_def("filesrc location={input_file} ! matroskademux ! jpegdec ! videoconvert ! videorate ! video/x-raw,framerate=10/1 ! theoraenc bitrate=8000  quality=63 ! oggmux ! filesink location={output_file}")


class MKV2WEBMTranscoder(AbstractTranscoder):

    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)
        self.set_pipeline_def("filesrc location={input_file} ! matroskademux ! jpegdec ! videoconvert ! vp8enc threads=4 ! webmmux ! filesink location={output_file}")


class MKV2MP4Transcoder(AbstractTranscoder):

    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)
        self.set_pipeline_def("filesrc location={input_file} ! matroskademux ! jpegdec ! videoconvert ! x264enc ! qtmux ! filesink location={output_file}")