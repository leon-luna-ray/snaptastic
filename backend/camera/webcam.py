import os
import platform
import threading
import time

import cv2

from .base import PHOTOS_DIR, CameraBackend, CameraError, new_photo_name

# Live view is re-encoded at a lower quality to keep the MJPEG stream light;
# saved photos use the full-quality frame.
LIVE_JPEG_QUALITY = 75
PHOTO_JPEG_QUALITY = 95
# Give up on the camera after this many failed reads in a row (about 2s).
MAX_FAILED_READS = 60


class WebcamCamera(CameraBackend):
    """A generic USB webcam read with OpenCV.

    A background thread reads frames continuously. The newest raw frame is kept
    for release(), and a JPEG copy is kept for the live view stream.
    """

    name = "webcam"

    def __init__(self, index=0, width=1920, height=1080):
        super().__init__()
        self.index = index
        self.width = width
        self.height = height
        self._capture = None
        self._thread = None
        self._running = False
        self._frame_lock = threading.Lock()
        self._raw_frame = None
        self._connect_lock = threading.Lock()

    def connect(self):
        with self._connect_lock:
            if self.connected:
                return
            self._stop_thread()
            # DirectShow opens most USB webcams faster and more reliably on Windows
            # than the default Media Foundation backend.
            api = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_ANY
            capture = cv2.VideoCapture(self.index, api)
            if not capture.isOpened():
                capture.release()
                self.error = f"No webcam found at index {self.index}. Is it plugged in?"
                raise CameraError(self.error)
            capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            ok, frame = capture.read()
            if not ok:
                capture.release()
                self.error = "The webcam opened but sent no picture"
                raise CameraError(self.error)

            self._capture = capture
            self._store_frame(frame)
            self.error = None
            self.connected = True
            self._running = True
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()

    def disconnect(self):
        with self._connect_lock:
            self._stop_thread()

    def release(self):
        if not self.connected:
            raise CameraError("Camera is not connected")
        with self._frame_lock:
            frame = None if self._raw_frame is None else self._raw_frame.copy()
        if frame is None:
            raise CameraError("No picture from the webcam yet")
        ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, PHOTO_JPEG_QUALITY])
        if not ok:
            raise CameraError("Could not encode the photo")
        os.makedirs(PHOTOS_DIR, exist_ok=True)
        name = new_photo_name(".jpg")
        with open(os.path.join(PHOTOS_DIR, name), "wb") as f:
            f.write(jpeg.tobytes())
        self.last_photo = name
        return name

    def _stop_thread(self):
        self._running = False
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=3)
        self._thread = None
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        self.connected = False
        self.latest_frame = None
        with self._frame_lock:
            self._raw_frame = None

    def _read_loop(self):
        failed_reads = 0
        while self._running:
            ok, frame = self._capture.read()
            if not ok:
                failed_reads += 1
                if failed_reads >= MAX_FAILED_READS:
                    self.error = "Lost connection to the webcam"
                    self.connected = False
                    self._running = False
                    break
                time.sleep(0.03)
                continue
            failed_reads = 0
            self._store_frame(frame)

    def _store_frame(self, frame):
        with self._frame_lock:
            self._raw_frame = frame
        ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, LIVE_JPEG_QUALITY])
        if ok:
            self.latest_frame = jpeg.tobytes()
            self.frame_id += 1
