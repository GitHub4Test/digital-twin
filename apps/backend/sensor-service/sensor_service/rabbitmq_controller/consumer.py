"""
Consumes the sessnor data messages from RabittMQ
"""

import asyncio
import json
import logging
import os

from aio_pika import IncomingMessage
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from sensor_service.db_controller.db_exceptions import DuplicateEventError
from sensor_service.db_controller.db_mgr import db_mgr
from sensor_service.rabbitmq_controller.rabbitmq_mgr import rabbitmq
from sensor_service.sensor_reading_mgr import SensorReadingMgr

logger = logging.getLogger(__name__)

RABBITMQ_QUEUE_SENSOR = os.getenv(
    "RABBITMQ_QUEUE_SENSOR", "sensor.readings"
)
RABBITMQ_QUEUE_SENSOR_DLQ = os.getenv(
    "RABBITMQ_QUEUE_SENSOR_DLQ", "sensor.readings.dlq"
)
RABBITMQ_DLX = os.getenv("RABBITMQ_DLX", "sensor.readings.dlx")


class DatabaseWriteError(Exception):
    pass


class RabbitMQConsumer:
    def __init__(self, sensor_reading_mgr: SensorReadingMgr, rabbitmq):
        # database connection
        self._sensor_reading_mgr = sensor_reading_mgr

        # RabbitMQ connection
        self._rabbitmq = rabbitmq
        self._queue = None

    async def initialize(self):
        """Initialize dependencies required by the consumer."""

        # RabbitMQ initialization
        await self._rabbitmq.connect()
        logger.info("Connected to RabbitMQ")

        await self._setup_rabbitmq()

    async def _setup_rabbitmq(self):
        # initiate dead letter queue exchange
        dlx = await self._rabbitmq.channel.declare_exchange(
            RABBITMQ_DLX,
            type="direct",
            durable=True,
        )

        # initiate dead letter queue
        dlq = await self._rabbitmq.channel.declare_queue(
            RABBITMQ_QUEUE_SENSOR_DLQ,
            durable=True,
        )

        await dlq.bind(
            dlx,
            routing_key=RABBITMQ_QUEUE_SENSOR_DLQ,
        )

        self._queue = await self._rabbitmq.channel.declare_queue(
            RABBITMQ_QUEUE_SENSOR,
            durable=True,
            arguments={
                "x-dead-letter-exchange": RABBITMQ_DLX,
                "x-dead-letter-routing-key": RABBITMQ_QUEUE_SENSOR_DLQ,
            },
        )
        logger.info("Sensor RabbitMQ consumer initialized")

    async def run(self):
        if self._queue is None:
            raise RuntimeError(
                "RabbitMQConsumer has not been initialized"
            )

        logger.info("Waiting for sensor events! Press CTRL+C to exit.")
        await self._queue.consume(self.handle_event)

        try:
            await asyncio.Future()
        finally:
            logger.info("Shutting down RabbitMQ consumer")
            await self.stop()
            logger.info("Consumer shutdown complete")

    async def stop(self):
        logger.info("Shutting down RabbitMQ consumer")

        await self._rabbitmq.close()

        logger.info("RabbitMQ consumer shutdown complete")

    async def handle_event(self, message: IncomingMessage):
        async with message.process(requeue=False):
            payload = json.loads(message.body.decode("utf-8"))

            event_id = payload["event_id"]

            logger.debug(
                "Received sensor event: %s", event_id,
            )
            self._sensor_reading_mgr.mark_reading_processed(
                event_id
            )

            logger.info("Processed sensor event: %s", event_id)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(DatabaseWriteError),
        reraise=True,
    )
    async def insert_reading_with_retry(self, payload: dict):
        try:
            self._sensor_reading_mgr.insert_reading(
                payload["event_id"],
                payload["timestamp"],
                payload["temperature"],
                payload["humidity"],
            )
        except DuplicateEventError:
            logger.info("Duplicate event ignored: %s", payload["event_id"])
        except Exception as e:
            raise DatabaseWriteError(str(e)) from e


async def run_rabbitmq_consumer():

    sensor_manager = SensorReadingMgr(db_mgr)
    sensor_manager.init_tables()

    consumer = RabbitMQConsumer(sensor_manager, rabbitmq)

    await consumer.initialize()
    await consumer.run()


if __name__ == "__main__":
    run_rabbitmq_consumer()
