from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image, ImageFilter
import PIL.ImageOps
import io

app = FastAPI()

# ADD THIS — fixes the browser error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageRequest(BaseModel):
    operation: str = Field(..., pattern="^(grayscale|blur|edge_detection|invert)$")
    blur_intensity: int = Field(default=2, ge=1, le=20)

@app.post("/process-image/")
async def process_image(
    file: UploadFile = File(...),
    operation: str = "grayscale",
    blur_intensity: int = 2
):
    params = ImageRequest(operation=operation, blur_intensity=blur_intensity)

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    if params.operation == "grayscale":
        result = image.convert("L")
    elif params.operation == "blur":
        result = image.filter(ImageFilter.GaussianBlur(radius=params.blur_intensity))
    elif params.operation == "edge_detection":
        result = image.convert("L").filter(ImageFilter.FIND_EDGES)
    elif params.operation == "invert":
        result = PIL.ImageOps.invert(image)

    output = io.BytesIO()
    result.save(output, format="PNG")
    output.seek(0)
    return StreamingResponse(output, media_type="image/png")