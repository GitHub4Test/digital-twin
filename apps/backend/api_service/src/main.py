"""
Application factory and main FastAPI app setup
"""

from fastapi import FastAPI
from src.db.database import db
from src.rabbitmq.rabbitmq import rabbitmq
from src.routes.common import router as common_router
from src.routes.sensor import router as sensor_router
from . import logger

app = FastAPI(
    title="Digital Twin Backend",
    description="Unified backend service for sensor data management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Digital Twin Team",
        "email": "admin@example.com",
    },
)

app.include_router(common_router)
app.include_router(sensor_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting backend application and initializing database")
    db.init()
    logger.info("Database initialized and backend is ready")
    await rabbitmq.connect()

@app.on_event("shutdown")
async def shutdown():
    db.close()
    await rabbitmq.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)