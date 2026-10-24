import datetime
import os
import threading
import time
from ctypes import c_long, c_longlong, create_string_buffer

from . import camera_control as cc

PHOTOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "photos")

PHOTO_EXTENSIONS = {
    cc.XSDK_IMAGEFORMAT_JPEG: ".JPG",
    cc.XSDK_IMAGEFORMAT_HEIF: ".HEIC",
}


class CameraError(Exception):
    pass


class CameraService:
    """Owns the single SDK session with the camera.

    The SDK isn't thread-safe, so every SDK call happens while holding self._lock.
    A background thread polls the camera's image buffer: live view frames are kept
    in memory for streaming, and photos taken with release() are saved to PHOTOS_DIR.
    """

    def __init__(self):
        self._control = None
        self._handle = c_longlong(0)
        self._lock = threading.Lock()
        self._thread = None
        self._running = False
        self._photo_saved = threading.Event()
        self.connected = False
        self.error = None
        self.latest_frame = None
        self.frame_id = 0
        self.last_photo = None

    def status(self):
        return {"connected": self.connected, "error": self.error, "last_photo": self.last_photo}

    def connect(self):
        if self.connected:
            return
        self.disconnect()  # clean up a session left over from a lost connection
        with self._lock:
            try:
                self._open_session()
            except CameraError as e:
                self.error = str(e)
                self._teardown()
                raise
            self.error = None
            self.connected = True
            self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def disconnect(self):
        self._running = False
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join()
            self._thread = None
        with self._lock:
            self._teardown()

    def release(self, timeout=10):
        if not self.connected:
            raise CameraError("Camera is not connected")
        self._photo_saved.clear()
        with self._lock:
            shot_option = c_long(0)
            status = c_long(0)
            result = self._control.release_ex(
                self._handle, cc.XSDK_RELEASE_EX_S1_ON_S2_ON_S2_OFF_S1_OFF, shot_option, status
            )
            if result != cc.XSDK_COMPLETE:
                raise CameraError(self._sdk_error("Shutter release"))
        # The photo arrives in the camera's buffer a moment later; the read loop saves it.
        if not self._photo_saved.wait(timeout):
            raise CameraError("The shutter fired but no photo arrived from the camera")
        return self.last_photo

    def _open_session(self):
        control = cc.CameraControl()
        if not control.load_library():
            raise CameraError("Could not load the Fujifilm SDK (is backend/camera/bundle in place?)")
        if control.init() != cc.XSDK_COMPLETE:
            raise CameraError("Could not initialize the Fujifilm SDK")
        self._control = control

        # Apple silicon Macs need at least 3s between XSDK_Init and XSDK_Detect.
        time.sleep(3)

        camera_count = c_long(0)
        ip_address = create_string_buffer(b"", 20)
        device_name = create_string_buffer(b"", 20)
        if control.detect(cc.XSDK_DSC_IF_USB, ip_address, device_name, camera_count) != cc.XSDK_COMPLETE:
            raise CameraError(self._sdk_error("Camera search"))
        if camera_count.value <= 0:
            raise CameraError("No camera found. Is it plugged in and set to USB TETHER SHOOTING AUTO?")

        device = create_string_buffer(b"ENUM:0", 10)
        camera_mode = c_long(0)
        if control.open(device, self._handle, camera_mode, None) != cc.XSDK_COMPLETE:
            raise CameraError(self._sdk_error("Opening the camera"))

        # The X-T3 only allows live view and remote shutter release in PC priority mode.
        if control.set_priority_mode(self._handle, cc.XSDK_PRIORITY_PC) != cc.XSDK_COMPLETE:
            raise CameraError(self._sdk_error("Switching to PC priority"))

        control.set_prop_l(self._handle, cc.API_CODE.API_CODE_SetLiveViewImageQuality.value, 1, cc.SDK_LIVEVIEW_QUALITY_FINE)
        control.set_prop_l(self._handle, cc.API_CODE.API_CODE_SetLiveViewImageSize.value, 1, cc.SDK_LIVEVIEW_SIZE_L)

        # StartLiveView returns BUSY unless the image buffer is empty.
        self._drain_buffer()
        if control.set_prop(self._handle, cc.API_CODE.API_CODE_StartLiveView.value, 0) != cc.XSDK_COMPLETE:
            raise CameraError(self._sdk_error("Starting live view"))

    def _teardown(self):
        if self._control is not None:
            if self._handle.value != 0:
                self._control.set_prop(self._handle, cc.API_CODE.API_CODE_StopLiveView.value, 0)
                self._drain_buffer()
                self._control.close(self._handle)
                self._handle = c_longlong(0)
            self._control.exit()
            self._control = None
        self.connected = False
        self.latest_frame = None

    def _drain_buffer(self):
        for _ in range(100):
            info = cc.ImageInformation()
            if self._control.read_image_info(self._handle, info) != cc.XSDK_COMPLETE:
                break
            if info.format & 0xFF == cc.XSDK_IMAGEFORMAT_NONE:
                break
            self._control.delete_image(self._handle)

    def _read_loop(self):
        while self._running:
            with self._lock:
                if not self._running:
                    break
                self._read_next_image()
            time.sleep(0.03)

    def _read_next_image(self):
        info = cc.ImageInformation()
        if self._control.read_image_info(self._handle, info) != cc.XSDK_COMPLETE:
            if self._control.err_code.value == cc.ERR_CODE.XSDK_ERRCODE_COMMUNICATION.value:
                self.error = "Lost connection to the camera"
                self.connected = False
                self._running = False
            return

        image_format = info.format & 0xFF
        if image_format == cc.XSDK_IMAGEFORMAT_NONE:
            return
        if image_format == cc.XSDK_IMAGEFORMAT_LIVE:
            data = self._read_image_data(info)
            if data is not None:
                self.latest_frame = data
                self.frame_id += 1
        elif image_format in PHOTO_EXTENSIONS:
            data = self._read_image_data(info)
            if data is not None:
                self._save_photo(data, PHOTO_EXTENSIONS[image_format])
        else:
            # RAW files and anything else: drop them so the buffer doesn't fill up.
            self._control.delete_image(self._handle)

    def _read_image_data(self, info):
        data = create_string_buffer(info.data_size)
        if self._control.read_image(self._handle, data, info.data_size) != cc.XSDK_COMPLETE:
            return None
        return data.raw

    def _save_photo(self, data, extension):
        os.makedirs(PHOTOS_DIR, exist_ok=True)
        name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] + extension
        with open(os.path.join(PHOTOS_DIR, name), "wb") as f:
            f.write(data)
        self.last_photo = name
        self._photo_saved.set()

    def _sdk_error(self, action):
        code = self._control.err_code.value
        try:
            name = cc.ERR_CODE(code).name
        except ValueError:
            name = hex(code)
        return f"{action} failed ({name})"


camera = CameraService()
