import os
import logging
import aio_pika

from api_gateway.models import SensorReading
from api_gateway.rabbitmq.rabbitmq import rabbitmq

RABBITMQ_QUEUE_SENSOR = os.getenv("RABBITMQ_QUEUE_SENSOR", "sensor.readings")

logger = logging.getLogger(__name__)

class SensorDataPublisher:
    async def publish_readings(self, reading: SensorReading):

        # Implement the logic to publish sensor readings to RabbitMQ
        queue_name = RABBITMQ_QUEUE_SENSOR
        logger.info(f"Publishing sensor event: event_id={reading.event_id}")

        # create message
        message = aio_pika.Message(
            body=reading.model_dump_json().encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
            message_id=reading.event_id,
        )

        # publish the message to the RabbitMQ queue
        await rabbitmq.channel.default_exchange.publish(
            message,
            routing_key=queue_name,
            mandatory=True,
        )
        logger.info(f"Sensor event published successfully: event_id={reading.event_id}")
