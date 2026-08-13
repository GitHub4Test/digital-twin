"""
Publish the messages to RabittMQ
"""

import asyncio
import json
import logging
import os

import aio_pika

from sensor_service.db_controller.db_mgr import db_mgr
from sensor_service.rabbitmq_controller.rabbitmq_mgr import rabbitmq
from sensor_service.sensor_reading_mgr import SensorReadingMgr

logger = logging.getLogger("outbox-publisher")

RABBITMQ_QUEUE_SENSOR = os.getenv(
    "RABBITMQ_QUEUE_SENSOR", "sensor.readings"
)


async def publish_sensor_event(data: dict):
    queue_name = RABBITMQ_QUEUE_SENSOR
    logger.info(
        f"Publishing sensor event: event_id={data.get('event_id')}"
    )

    message = aio_pika.Message(
        body=json.dumps(data).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        content_type="application/json",
        message_id=data["event_id"],
    )

    await rabbitmq.channel.default_exchange.publish(
        message,
        routing_key=queue_name,
        mandatory=True,
    )
    logger.info(
        f"Sensor event published successfully: event_id={data.get('event_id')}"
    )


async def publish_outbox_events():
    logger.info("Starting outbox event publisher")
    while True:
        try:
            events = SensorReadingMgr(db_mgr).get_pending_outbox_events(
                limit=10
            )
            logger.info(f"Processing {len(events)} pending outbox events")

            for event in events:
                try:
                    logger.info(
                        f"Publishing outbox event: id={event['id']}, aggregate_id={event.get('aggregate_id')}"
                    )
                    await publish_sensor_event(
                        json.loads(event["payload"])
                    )

                    SensorReadingMgr(db_mgr).mark_outbox_event_published(
                        event["id"]
                    )

                    logger.info(
                        "Published outbox event id=%s aggregate_id=%s",
                        event["id"],
                        event.get("aggregate_id"),
                    )
                except Exception as e:
                    SensorReadingMgr(db_mgr).increment_outbox_retry(
                        event["id"]
                    )
                    logger.exception(
                        "Failed to publish outbox event id=%s: %s",
                        event["id"],
                        e,
                    )
        except Exception as e:
            logger.exception("Outbox publisher loop failed: %s", e)

        await asyncio.sleep(5)


async def main():
    logging.basicConfig(level=logging.INFO)

    logger.info("Starting outbox publisher")

    await rabbitmq.connect()

    try:
        await publish_outbox_events()
    finally:
        await rabbitmq.close()


if __name__ == "__main__":
    asyncio.run(main())
