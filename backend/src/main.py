# import models

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
# from database import SessionLocal, engine
from typing import Annotated
# from sqlalchemy.orm import Session

from camera.service import PHOTOS_DIR, CameraError, camera


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Release the camera session when the server stops.
    camera.disconnect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(PHOTOS_DIR, exist_ok=True)
app.mount("/photos", StaticFiles(directory=PHOTOS_DIR), name="photos")

# models.Base.metadata.create_all(bind=engine)

@app.get("/api/hello")
def hello():
    return {"message": "Hello World"}


@app.get("/api/camera/status")
def camera_status():
    return camera.status()


# Plain `def` (not `async def`) endpoints run in a thread pool, so the slow
# camera calls below don't block the server.
@app.post("/api/camera/connect")
def camera_connect():
    try:
        camera.connect()
    except CameraError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    return camera.status()


@app.post("/api/camera/disconnect")
def camera_disconnect():
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
