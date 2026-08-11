"""
Application factory and main FastAPI app setup
"""

from fastapi import FastAPI
from api_gateway.rabbitmq import rabbitmq
from api_gateway.routers.health_check_router import router as common_router
from api_gateway.routers.sensor_router import sensorapirouter
from . import logger

app = FastAPI(
    title="Digital Twin API Gateway",
    description="API Gateway service for sensor data management",
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
app.include_router(sensorapirouter)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting backend application and connecting to rabbitmq")
    await rabbitmq.connect()

@app.on_event("shutdown")
async def shutdown():
    logger.info("Closing connection with rabbitmq")
    await rabbitmq.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)