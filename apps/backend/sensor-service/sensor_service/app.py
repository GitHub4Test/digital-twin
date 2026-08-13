# app.py
import asyncio
import uvicorn

from fastapi import FastAPI

from sensor_service.grpc_server import run_grpc_server
from sensor_service.rabbitmq_controller.consumer import (
    run_rabbitmq_consumer,
)
from sensor_service.routers.routes import router

api = FastAPI(
    title="Sensor Service API",
    description="API for Sensor Service",
    version="1.0.0",
)

api.include_router(router)


async def run_api_server():
    config = uvicorn.Config(
        app=api,
        host="0.0.0.0",
        port=8001,
        log_level="info",
    )

    server = uvicorn.Server(config)

    await server.serve()


async def main():
    await asyncio.gather(
        run_grpc_server(),
        run_rabbitmq_consumer(),
        run_api_server(),
    )


if __name__ == "__main__":
    asyncio.run(main())
