import uuid
import logging
from datetime import datetime, timezone

import grpc
from google.protobuf.timestamp_pb2 import Timestamp

from sensor_service.generated.sensor.v1 import sensor_pb2, sensor_pb2_grpc
from sensor_service.db_controller.db_mgr import db_mgr

logger = logging.getLogger(__name__)

def _to_proto_reading(reading: dict) -> sensor_pb2.SensorReadingResponse:
    ts = Timestamp()
    ts.FromDatetime(reading["timestamp"])
    return sensor_pb2.SensorReadingResponse(
        event_id=reading["event_id"],
        timestamp=ts,
        temperature=reading["temperature"],
        humidity=reading["humidity"],
        status=reading.get("status", "OK"),
    )


class SensorServicer(sensor_pb2_grpc.SensorServiceServicer):
    def __init__(self):
        self.db_mgr = db_mgr

    def SubmitReading(self, request, context):
        reading = {
            "event_id": request.event_id,
            "timestamp": request.timestamp.ToDatetime(tzinfo=timezone.utc),
            "temperature": request.temperature,
            "humidity": request.humidity,
            "status": request.status,
        }
        payload = _to_proto_reading(reading)

        event_payload = payload.model_dump(mode="json")

        try:
            logger.info(f"Creating reading and outbox event: event_id={event_id}, temp={reading.temperature}C")
            self.db_mgr.create_reading_and_outbox_event(
                event_id=event_id,
                timestamp=event_payload["timestamp"],
                temperature=event_payload["temperature"],
                humidity=event_payload["humidity"],
                outbox_payload=event_payload,
            )
            logger.info(f"Sensor reading accepted for processing: event_id={event_id}")
        except DuplicateEventError:
            logger.warning(f"Duplicate sensor reading received: event_id={event_id}")
        except Exception as e:
            logger.error(f"Failed to create sensor reading event: event_id={event_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def ListReadings(self, request, context):
        try:
            logger.info(f"Retrieving sensor readings: limit={request.limit}")
            readings = self.db_mgr.get_readings(request.limit)
            logger.info(f"Retrieved {len(readings)} sensor readings")

            for reading in readings:
                yield _to_proto_reading(reading)
        except Exception as e:
            logger.error(f"Failed to retrieve sensor readings: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")            