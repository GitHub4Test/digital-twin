"""
Consumes the sessnor data messages from RabittMQ
"""

import json
import os
import asyncio
import logging

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from sensor_service.db.database import db
from sensor_service.db.exceptions import DuplicateEventError
from sensor_service.rabbitmq.rabbitmq import rabbitmq

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

class RabbitMQConsumer:

    def __init__(self):

        # database connection
        self._db = db
        self._db.init()
        logger.info("Database initialized")    

        # RabbitMQ connection
        self._rabbitmq = rabittmq
        self._rabbitmq.connect()
        logger.info("Connected to RabbitMQ")

        self._init_rabbitmq_consumer()

    async def init_rabbitmq_consumer(self):
        # initiate dead letter queue exchange
        dlx = await self.rabbitmq.channel.declare_exchange(
            RABBITMQ_DLX,
            type="direct",
            durable=True,
        )
        
        # initiate dead letter queue
        dlq = await rabbitmq.channel.declare_queue(
            RABBITMQ_QUEUE_SENSOR_DLQ,
            durable=True,
        )

        await dlq.bind(
            dlx,
            routing_key=RABBITMQ_QUEUE_SENSOR_DLQ,
        )

        self.queue = await rabbitmq.channel.declare_queue(
            RABBITMQ_QUEUE_SENSOR,
            durable=True,
            arguments={
                "x-dead-letter-exchange": RABBITMQ_DLX,
                "x-dead-letter-routing-key": RABBITMQ_QUEUE_SENSOR_DLQ,
            },  
        )
        logger.info("Sensor event consumer is setup.")

    async def run(self):

        logger.info("Waiting for messages! Press CTRL+C to exit.")            
        await self.queue.consume(self.handle_event)
        
        try:
            await asyncio.Future()
        finally:
            logger.info("Shutting down RabbitMQ consumer")
            await self.rabbitmq.close()
            logger.info("Consumer shutdown complete")

    async def handle_event(self, message):
        async with message.process(requeue=False):
            payload = json.loads(message.body.decode())

            db.mark_reading_processed(payload["event_id"])

            logger.info("Processed sensor event: %s", payload["event_id"])


if __name__ == "__main__":
    rabbitMQInstance = RabbitMQConsumer()
    asyncio.run(rabbitMQInstance.run())