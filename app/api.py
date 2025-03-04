import os
import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from models.segmentation import Segmenter  # Ensure this module exists and is implemented

router = APIRouter()

# Initialize your models once so they're reused for every request
segmenter = Segmenter(model_path="path/to/your/segmentation_model")

@router.post("/process")
async def process_image(file: UploadFile = File(...), background: str = "data/stock_backgrounds/default.jpg"):
    """
    Endpoint to process an image:
      - Upload the image.
      - Segment the foreground using the segmentation model.
      - Replace the background using a stock background or provided background.
    """
    try:
        file_contents = await file.read()
        image = Image.open(io.BytesIO(file_contents)).convert("RGBA")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing the image: {str(e)}")
    
    # Perform segmentation (assuming segment returns a processed foreground image or mask)
    segmented_foreground = segmenter.segment(image)
    

    # Create a composite image by replacing the background
    composite_image = background_creator.create_background(
        background=background,
        foreground=segmented_foreground  # This might be a mask or an RGBA image, adjust as needed
    )

    
    # Save the composite image to the output folder
    composite_output_path = os.path.join("data", "output", "composite.png")
    composite_image.save(composite_output_path)
    
    return JSONResponse(content={"message": "Background replaced", "output": composite_output_path})