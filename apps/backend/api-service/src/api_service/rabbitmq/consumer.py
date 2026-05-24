"""
Consumes the sessnor data messages from RabittMQ
"""

import json
import os
import asyncio
import logging

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from api_service.db.database import db
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
            payload["timestamp"],
            payload["temperature"],
            payload["humidity"],
        )
    except Exception as e:
        raise DatabaseWriteError(str(e)) from e

async def handle_sensor_event(message):
    async with message.process(requeue=False):
        payload = json.loads(message.body.decode())

        logger.info("Received sensor event: %s", payload)

        await insert_reading_with_retry(payload)

async def start_sensor_consumer():
    await rabbitmq.channel.declare_exchange(
        RABBITMQ_DLX,
        type="direct",
        durable=True,
    )

    await rabbitmq.channel.declare_queue( 
        RABBITMQ_QUEUE_SENSOR_DLQ,
        durable=True,
        arguments={
            "x-message-ttl": 60000,  # 1 minute TTL for messages in DLQ
            "x-dead-letter-exchange": RABBITMQ_DLX,
            "x-dead-letter-routing-key": RABBITMQ_QUEUE_SENSOR,
        }
    )

    await dlq.bind(
        RABBITMQ_DLX,
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

    await queue.consume(handle_sensor_event)

async def main():
    db.init()

    await rabbitmq.connect()
    await start_sensor_consumer()

    print("[*] Waiting for messages. To exit press CTRL+C")

    try:
        await asyncio.Future()
    finally:
        await rabbitmq.close()

if __name__ == "__main__":
    asyncio.run(main())