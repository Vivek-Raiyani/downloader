from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
import os
from typing import Dict, Any
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from downloader import get_downloader
from storage import storage_manager
from config import settings

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(
    storage_manager.cleanup_old_files, 
    'interval', 
    seconds=settings.CLEANUP_INTERVAL_SECONDS
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the scheduler
    print(f"\n[SYSTEM] Starting scheduler with interval: {settings.CLEANUP_INTERVAL_SECONDS}s")
    scheduler.start()
    
    # Run one cleanup immediately on start so the user can see it working
    print("[SYSTEM] Running initial cleanup check...")
    storage_manager.cleanup_old_files()
    
    yield
    # Shutdown: Stop the scheduler
    scheduler.shutdown()

app = FastAPI(title="Universal Media Downloader", debug=settings.DEBUG, lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task store (Use Redis for production)
tasks: Dict[str, Dict[str, Any]] = {}

class DownloadRequest(BaseModel):
    url: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float = 0.0
    result: Dict[str, Any] | None = None
    error: str | None = None

def download_task(task_id: str, url: str):
    tasks[task_id]["status"] = "downloading"
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%', '')
                tasks[task_id]["progress"] = float(p)
            except:
                pass

    downloader = get_downloader()
    result = downloader.download(url, progress_hook=progress_hook)
    
    if result.get("success"):
        tasks[task_id]["status"] = "processing"
        local_path = result["filepath"]
        
        # Handle S3 upload if enabled
        if settings.S3_ENABLED:
            tasks[task_id]["status"] = "uploading"
            s3_url = storage_manager.upload_file(local_path)
            if s3_url:
                result["s3_url"] = s3_url
                storage_manager.delete_local_file(local_path)
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100.0
        tasks[task_id]["result"] = result
    else:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = result.get("error")

@app.post("/api/download", response_model=TaskStatus)
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0.0,
        "result": None,
        "error": None
    }
    background_tasks.add_task(download_task, task_id, request.url)
    return tasks[task_id]

@app.get("/api/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

# Serve downloaded files
app.mount("/downloads", StaticFiles(directory=settings.DOWNLOAD_DIR), name="downloads")

# Serve static files for frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
