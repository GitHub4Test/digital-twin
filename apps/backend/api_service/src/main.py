"""
Application factory and main FastAPI app setup
"""

from fastapi import FastAPI
import os
import sys
from src.database import Database
from src.routes import router

from . import logger

app = FastAPI(
    title="Digital Twin Backend",
    description="Unified backend service for sensor data management",
    version="1.0.0"
)

# Include routes
app.include_router(router)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on service startup"""
    logger.info("Starting backend application and initializing database")
    db = Database()
    db.init()
    logger.info("Database initialized and backend is ready")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
