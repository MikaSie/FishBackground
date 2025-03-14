import os
import io
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from models.segmentation import Segmenter 

app = FastAPI(title= "Background Remover API", description="API to remove background from images")

app.mount("/stock_backgrounds", StaticFiles(directory= os.path.join('data', 'stock_backgrounds')), name= "stock_backgrounds")

segmenter = Segmenter(model_name='u2net_human_seg')

@app.get("/")
async def root():
    return {"message": "Welcome to Background Remover API"}

@app.post("/process_image")
async def process_image(background: UploadFile = File(...), foreground: UploadFile = File(...)):
    background_image = Image.open(io.BytesIO(await background.read())).convert("RGBA")
    foreground_image = Image.open(io.BytesIO(await foreground.read())).convert("RGBA")
    
    segmented_foreground = segmenter.segment(foreground_image)

    combined_image = segmenter.combine_foreground_and_background(background_image, segmented_foreground)
    
    output_bytes = io.BytesIO()
    combined_image.save(output_bytes, format='PNG')
    output_bytes.seek(0)

    return StreamingResponse(output_bytes, media_type="image/png")

@app.get("/available_stock_backgrounds")
async def available_stock_backgrounds():
    backgrounds_dir = os.path.join('data', 'stock_backgrounds')
    filenames = os.listdir(backgrounds_dir)
    # Construct URLs for each background image
    urls = [f"/stock_backgrounds/{filename}" for filename in filenames]
    return JSONResponse({"stock_backgrounds": urls})