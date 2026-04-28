"""
Consumes the sessnor data messages from RabittMQ
"""

import json
import os
import asyncio

from api_service.db.database import db
from api_service.rabbitmq.rabbitmq import rabbitmq

RABBITMQ_QUEUE_SENSOR = os.getenv("RABBITMQ_QUEUE_SENSOR", "sensor.readings")

async def handle_sensor_event(message):
    async with message.process():
        payload = json.loads(message.body.decode())

        print("Received sensor event:", payload)

        db.insert_reading(
            payload["timestamp"],
            payload["temperature"],
            payload["humidity"]
        )

async def start_sensor_consumer():
    queue = await rabbitmq.channel.declare_queue(
        RABBITMQ_QUEUE_SENSOR,
        durable=True,
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