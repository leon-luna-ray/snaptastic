"""Pick the camera backend from the SNAPTASTIC_CAMERA environment variable.

  SNAPTASTIC_CAMERA=webcam  (default) a generic USB webcam via OpenCV
                            SNAPTASTIC_WEBCAM_INDEX picks which one (default 0)
  SNAPTASTIC_CAMERA=fuji    a Fujifilm camera via the XAPI SDK
"""
import os

from .base import PHOTOS_DIR, CameraBackend, CameraError


def create_camera() -> CameraBackend:
    kind = os.environ.get("SNAPTASTIC_CAMERA", "webcam").strip().lower()
    if kind == "fuji":
        # Imported only when selected, so machines without the SDK still run.
        from .fuji import FujiCamera

        return FujiCamera()
    if kind == "webcam":
        from .webcam import WebcamCamera

        return WebcamCamera(index=int(os.environ.get("SNAPTASTIC_WEBCAM_INDEX", "0")))
    raise ValueError(f"Unknown SNAPTASTIC_CAMERA {kind!r} (expected 'webcam' or 'fuji')")


__all__ = ["PHOTOS_DIR", "CameraBackend", "CameraError", "create_camera"]
