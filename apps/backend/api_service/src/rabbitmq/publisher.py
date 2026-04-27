"""
Publish the messages to RabittMQ
"""

import os
import json
import aio_pika
from src.rabbitmq.rabbitmq import rabbitmq

RABBITMQ_QUEUE_SENSOR = os.getenv("RABBITMQ_QUEUE_SENSOR", "sensor.readings")

async def publish_sensor_event(data: dict):
    queue_name = RABBITMQ_QUEUE_SENSOR

    await rabbitmq.channel.declare_queue(
        queue_name,
        durable=True,
    )

    message = aio_pika.Message(
        body=json.dumps(data).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        content_type="application/json",
    )

    await rabbitmq.channel.default_exchange.publish(
        message,
        routing_key=queue_name,
    )
