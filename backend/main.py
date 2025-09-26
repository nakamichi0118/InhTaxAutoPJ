from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from loguru import logger

# Try to load dotenv if available (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # In production, environment variables are set by the platform

from api import documents, ocr, health
from core.config import settings

# Configure logging
logger.add("logs/app.log", rotation="500 MB", retention="10 days", level="INFO")

# Create FastAPI app
app = FastAPI(
    title="相続税申告書類処理システム",
    description="相続税申告に関する書類を自動読み取りし、財産区分別に分類・出力するシステム",
    version="1.0.0"
)

# Configure CORS - be more permissive for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["ocr"])

@app.on_event("startup")
async def startup_event():
    logger.info("相続税申告書類処理システム起動")
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("相続税申告書類処理システム終了")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )