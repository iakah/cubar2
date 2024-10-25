from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from nerf_processing import start_3d_reconstruction
from celery.result import AsyncResult
from pyngrok import ngrok
import os
import shutil
from starlette.responses import JSONResponse
import uvicorn

app = FastAPI()

ngrok.set_auth_token("2nVszk2rwTFvOGG5fmwMKjpnrzL_3rSgmtXysWjqkBikBSNQL")

current_dir = os.path.dirname(os.path.abspath(__file__))  # app folder
parent_dir = os.path.dirname(current_dir)  # parent of app folder
static_dir = os.path.join(parent_dir, "static")  # Adjust this path for static files


UPLOAD_DIR = "uploads/"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Start ngrok and get the public URL
port = 8000
public_url = ngrok.connect(str(port)).public_url
print(f"ngrok tunnel available at: {public_url}")

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(static_dir, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content=f"Error: HTML file not found at {html_path}", status_code=404)

@app.post("/upload/")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Start background task for 3D model processing
    task = start_3d_reconstruction.delay(file_location)

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
    # Run the FastAPI app with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
