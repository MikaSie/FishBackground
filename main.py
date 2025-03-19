import os
import io
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from models.segmentation import Segmenter 

app = FastAPI(title= "Background Remover API", description="API to remove background from images")
app.mount("/static", StaticFiles(directory= "static", html= True), name = "static")

segmenter = Segmenter(model_name='u2net_human_seg')

@app.get("/")
def serve_index():
    with open("static/index.html") as f:
        return HTMLResponse(f.read())

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
    return JSONResponse({"stock_backgrounds": filenames})


app.mount("/stock_backgrounds", StaticFiles(directory= os.path.join('data', 'stock_backgrounds')), name= "stock_backgrounds")
