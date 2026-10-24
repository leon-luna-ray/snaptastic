# Snaptastic
Photo booth app.

[https://snaptastic.fly.dev/](https://snaptastic.fly.dev/)

## Technologies

### Backend
- FastAPI
- Python
- Fujifilm X Series Camera Control SDK
- Fly.io

### Frontend
- Vue.js
- CSS3
- HTML5
- JavaScript

## Running locally

The backend runs directly on your Mac (not in Docker) because Docker on macOS can't reach USB devices like the camera.

### Camera setup (Fujifilm X-T3)
1. On the camera: SET UP → CONNECTION SETTING → PC CONNECTION MODE → **USB TETHER SHOOTING AUTO** (or **PC SHOOT AUTO** on older firmware).
2. Plug the camera into the Mac with a USB data cable.
3. Quit Image Capture, Photos, X Acquire, Lightroom, or anything else that might grab the camera.

The Fujifilm SDK libraries are not in git. Unzip `REDISTRIBUTABLES/macOS/SDK_13400.zip` from the SDK and copy the contents of its `SDK_13400/` folder into `backend/camera/bundle/`.

### Backend
```
cd backend
venv/bin/python run.py
```
Runs on http://localhost:8080 (API docs at http://localhost:8080/docs). Photos are saved to `backend/photos/`.

### Frontend (and Postgres)
```
docker compose up --build
```
Open http://localhost:5173, click **Connect camera**, then **Shutter**.
