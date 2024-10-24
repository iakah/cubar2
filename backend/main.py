from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from nerf_processing import process_3d_model_task
from celery.result import AsyncResult
import os
import shutil
from starlette.responses import JSONResponse

app = FastAPI()

UPLOAD_DIR = "uploads/"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r") as f:
        return f.read()


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Start background task for 3D model processing
    task = process_3d_model_task.delay(file_location)

    return JSONResponse({"task_id": task.id, "status": "Processing started."})


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"status": "Processing", "progress": task_result.info}
    elif task_result.state == "SUCCESS":
        return {"status": "Completed", "result": task_result.result}
    else:
        raise HTTPException(status_code=500, detail="Task failed")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
