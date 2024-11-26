from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/api")
def read_root():
    return {"message": "Welcome to the Photo Booth App"}

# Serve the frontend
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")