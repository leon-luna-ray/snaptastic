import asyncio
import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from camera import PHOTOS_DIR, CameraError, create_camera

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = os.path.join(BACKEND_DIR, "..", "frontend", "dist")
# How often the watchdog retries when the camera isn't connected.
RECONNECT_SECONDS = 5

camera = create_camera()


class Watchdog:
    """Keeps the camera connected without anyone pressing a button: connects at
    startup and reconnects after the camera is unplugged or drops out.
    A manual disconnect pauses it until the next manual connect."""

    def __init__(self):
        self.enabled = True
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=RECONNECT_SECONDS + 15)

    def _run(self):
        while not self._stop.is_set():
            if self.enabled and not camera.connected:
                try:
                    camera.connect()
                except CameraError:
                    pass  # camera.error holds the message for /api/camera/status
                except Exception as e:  # never let the watchdog thread die
                    camera.error = f"Camera error: {e}"
            self._stop.wait(RECONNECT_SECONDS)


watchdog = Watchdog()


@asynccontextmanager
async def lifespan(app: FastAPI):
    watchdog.start()
    yield
    # Release the camera session (and the Fujifilm SDK) when the server stops.
    watchdog.stop()
    camera.shutdown()


app = FastAPI(lifespan=lifespan)

# Only needed for the Vite dev server; the kiosk loads the UI from this server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(PHOTOS_DIR, exist_ok=True)
app.mount("/photos", StaticFiles(directory=PHOTOS_DIR), name="photos")


@app.get("/api/health")
def health():
    return {"ok": True, "camera": camera.status()}


@app.get("/api/camera/status")
def camera_status():
    return camera.status()


# Plain `def` (not `async def`) endpoints run in a thread pool, so the slow
# camera calls below don't block the server.
@app.post("/api/camera/connect")
def camera_connect():
    watchdog.enabled = True
    try:
        camera.connect()
    except CameraError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    return camera.status()


@app.post("/api/camera/disconnect")
def camera_disconnect():
    watchdog.enabled = False
    camera.disconnect()
    return camera.status()


@app.post("/api/camera/release")
def camera_release():
    try:
        photo = camera.release()
    except CameraError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return {"photo": photo}


@app.get("/api/camera/live")
async def camera_live():
    if not camera.connected:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Camera is not connected")

    # MJPEG stream: a never-ending response where each part is one JPEG frame.
    # Browsers display it directly in an <img> tag.
    async def frames():
        last_frame_id = None
        while camera.connected:
            frame = camera.latest_frame
            if frame is not None and camera.frame_id != last_frame_id:
                last_frame_id = camera.frame_id
                yield (
                    b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                    + str(len(frame)).encode()
                    + b"\r\n\r\n"
                    + frame
                    + b"\r\n"
                )
            await asyncio.sleep(0.03)

    return StreamingResponse(frames(), media_type="multipart/x-mixed-replace; boundary=frame")


# The built booth UI (`pnpm build` in frontend/). Mounted last so /api and
# /photos win. Skipped when there's no build, e.g. while using the Vite dev server.
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
