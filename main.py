from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import cv2
import numpy as np
import io

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="upload.html"
    )

@app.get("/upload_image", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="upload.html"
    )

@app.post("/process")
async def process_image(file: UploadFile = File(...)):
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, buffer = cv2.imencode(".jpg", processed)
    img_bytes = io.BytesIO(buffer.tobytes())
    return StreamingResponse(img_bytes, media_type="image/jpeg",
        headers={"Content-Disposition": "attachment; filename=edited.jpg"})