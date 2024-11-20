from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, RedirectResponse
import os

app = FastAPI()

# Check if running in development mode
is_dev = os.getenv("DEV", "false").lower() == "true"

if not is_dev:
    # Mount the static files directory for production
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

    @app.get("/")
    def read_root():
        return FileResponse("frontend/dist/index.html")

    @app.get("/{full_path:path}")
    def read_root(full_path: str):
        return FileResponse("frontend/dist/index.html")
else:
    @app.get("/")
    def read_root():
        return RedirectResponse(url="http://localhost:8080")

    @app.get("/{full_path:path}")
    def read_root(full_path: str):
        return RedirectResponse(url=f"http://localhost:8080/{full_path}")