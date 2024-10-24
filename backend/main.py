from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from nerf_processing import process_3d_model
import uvicorn
import os

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r") as f:
        return f.read()


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Save uploaded file
    upload_path = f"uploads/{file.filename}"
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    # Trigger NeRF processing
    output_path = process_3d_model(upload_path)

    # Return output model file path (to be displayed in frontend)
    return {"model_path": output_path}


if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    uvicorn.run(app, host="0.0.0.0", port=8000)
