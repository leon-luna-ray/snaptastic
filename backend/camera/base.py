import datetime
import os

PHOTOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "photos")


class CameraError(Exception):
    pass


class CameraBackend:
    """What the API needs from a camera. Fujifilm and webcam backends implement this.

    Attributes the API reads directly:
      connected    -- True while a session is open and frames are arriving
      error        -- last error message, or None
      latest_frame -- most recent live view frame as JPEG bytes, or None
      frame_id     -- increases with every new live view frame
      last_photo   -- file name (in PHOTOS_DIR) of the last photo taken
    """

    name = "camera"

    def __init__(self):
        self.connected = False
        self.error = None
        self.latest_frame = None
        self.frame_id = 0
        self.last_photo = None

    def status(self):
        return {
            "camera": self.name,
            "connected": self.connected,
            "error": self.error,
            "last_photo": self.last_photo,
        }

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def release(self):
        """Take a photo, save it to PHOTOS_DIR and return its file name."""
        raise NotImplementedError

    def shutdown(self):
        """Called once when the server stops."""
        self.disconnect()


def new_photo_name(extension):
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] + extension
