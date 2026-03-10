from fastapi import FastAPI, UploadFile, File, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
import time

from database import init_db, create_task, get_task, get_all_tasks
from ai_pipeline import start_processing

app = FastAPI(title="Audio Summarizer")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory="templates")
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/history", response_class=HTMLResponse)
async def read_history(request: Request):
    tasks = get_all_tasks()
    return templates.TemplateResponse("history.html", {"request": request, "tasks": tasks})

@app.post("/api/upload")
async def upload_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith((".mp3", ".wav", ".m4a")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .mp3, .wav, and .m4a are supported.")
        raise HTTPException(status_code=400, detail="Invalid file type. Only .mp3, .wav, and .m4a are supported.")
    file_path = os.path.join(UPLOAD_DIR, f"{time.time()}_{file.filename}")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    task_id = create_task(file.filename)
    task_id = create_task(file.filename)
    start_processing(task_id, file_path)
    start_processing(task_id, file_path)

    return JSONResponse(content={"task_id": task_id, "message": "File uploaded successfully."})

@app.get("/api/status/{task_id}")
async def get_audio_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
