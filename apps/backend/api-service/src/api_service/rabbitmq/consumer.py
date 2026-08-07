"""
Consumes the sessnor data messages from RabittMQ
"""

import json
import os
import asyncio
import logging

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from api_service.db.database import db
from api_service.db.exceptions import DuplicateEventError
from api_service.rabbitmq.rabbitmq import rabbitmq

logger = logging.getLogger(__name__)

RABBITMQ_QUEUE_SENSOR = os.getenv("RABBITMQ_QUEUE_SENSOR", "sensor.readings")
RABBITMQ_QUEUE_SENSOR_DLQ = os.getenv("RABBITMQ_QUEUE_SENSOR_DLQ", "sensor.readings.dlq")
RABBITMQ_DLX = os.getenv("RABBITMQ_DLX", "sensor.readings.dlx")

class DatabaseWriteError(Exception):
    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(DatabaseWriteError),
    reraise=True,
)
async def insert_reading_with_retry(payload: dict):
    try:
        db.insert_reading(
            payload["event_id"],
            payload["timestamp"],
            payload["temperature"],
            payload["humidity"],
        )
    except DuplicateEventError:
        logger.info("Duplicate event ignored: %s", payload["event_id"])        
    except Exception as e:
        raise DatabaseWriteError(str(e)) from e

async def handle_sensor_event(message):
    async with message.process(requeue=False):
        payload = json.loads(message.body.decode())

        db.mark_reading_processed(payload["event_id"])

        logger.info("Processed sensor event: %s", payload["event_id"])

async def start_sensor_consumer():
    logger.info("Starting sensor event consumer")
    logger.info(f"Consumer queue: {RABBITMQ_QUEUE_SENSOR}")
    
    dlx = await rabbitmq.channel.declare_exchange(
        RABBITMQ_DLX,
        type="direct",
        durable=True,
    )
    logger.info(f"Dead-letter exchange declared: {RABBITMQ_DLX}")

    dlq = await rabbitmq.channel.declare_queue(
        RABBITMQ_QUEUE_SENSOR_DLQ,
        durable=True,
    )

    await dlq.bind(
        dlx,
        routing_key=RABBITMQ_QUEUE_SENSOR_DLQ,
    )
   
    queue = await rabbitmq.channel.declare_queue(
        RABBITMQ_QUEUE_SENSOR,
        durable=True,
        arguments={
            "x-dead-letter-exchange": RABBITMQ_DLX,
            "x-dead-letter-routing-key": RABBITMQ_QUEUE_SENSOR_DLQ,
        },  
    )
    logger.info(f"Sensor queue declared: {RABBITMQ_QUEUE_SENSOR}")

    await queue.consume(handle_sensor_event)
    logger.info("Sensor event consumer started and listening")

async def main():
    logger.info("Initializing RabbitMQ consumer application")
    db.init()
    logger.info("Database initialized")

    await rabbitmq.connect()
    logger.info("Connected to RabbitMQ")
    
    await start_sensor_consumer()

    logger.info("Waiting for messages. To exit press CTRL+C")

    try:
        await asyncio.Future()
    finally:
        logger.info("Shutting down RabbitMQ consumer")
        await rabbitmq.close()
        logger.info("Consumer shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())