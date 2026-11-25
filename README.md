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

## Cameras

The backend talks to one camera, chosen with the `SNAPTASTIC_CAMERA` environment variable:

- `webcam` (default): any USB webcam, read with OpenCV. Set `SNAPTASTIC_WEBCAM_INDEX` (default `0`) if you have more than one.
- `fuji`: a Fujifilm camera through the Fujifilm SDK (setup below).

The backend connects to the camera by itself at startup and reconnects if it's unplugged.

## Kiosk (Windows)

See [kiosk/windows/README.md](kiosk/windows/README.md) for running the booth full screen and locked down with Edge and Windows Assigned Access.

## Running locally on Windows

Needs Python 3.12 and Node.js (`winget install Python.Python.3.12 OpenJS.NodeJS.LTS`).

```powershell
# Backend: http://localhost:8080
py -3.12 -m venv backend\.venv
backend\.venv\Scripts\pip install -r backend\requirements.txt
cd backend; .venv\Scripts\python run.py

# Frontend (second terminal): http://localhost:5173, with hot reload
cd frontend; npx pnpm@9 install; npx pnpm@9 dev
```

Or build the UI once (`npx pnpm@9 build`) and the backend serves it at http://localhost:8080.

## Running locally on macOS

The backend runs directly on your Mac (not in Docker) because Docker on macOS can't reach USB devices like the camera.

### Camera setup (Fujifilm X-T3)
1. On the camera: SET UP → CONNECTION SETTING → PC CONNECTION MODE → **USB TETHER SHOOTING AUTO** (or **PC SHOOT AUTO** on older firmware).
2. Plug the camera into the Mac with a USB data cable.
3. Quit Image Capture, Photos, X Acquire, Lightroom, or anything else that might grab the camera.

The Fujifilm SDK libraries are not in git. Unzip `REDISTRIBUTABLES/macOS/SDK_13400.zip` from the SDK and copy the contents of its `SDK_13400/` folder into `backend/camera/bundle/`.

### Backend
```
cd backend
SNAPTASTIC_CAMERA=fuji venv/bin/python run.py
```
Runs on http://localhost:8080 (API docs at http://localhost:8080/docs). Photos are saved to `backend/photos/`. Leave out `SNAPTASTIC_CAMERA=fuji` to use a webcam instead.

### Frontend (and Postgres)
```
docker compose up --build
```
Open http://localhost:5173 and tap the screen to take a photo.
