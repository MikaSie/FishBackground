from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(
    title="FishBackground API",
    description="An API for background replacement on fisherman images using segmentation models.",
    version="0.1.0"
)

# Include the routes defined in api.py
app.include_router(api_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)