import os
import logging

import grpc

from api_gateway.generated.sensor.v1 import sensor_pb2, sensor_pb2_grpc
from api_gateway.models import SensorReadingResponse

logger = logging.getLogger(__name__)

SENSOR_SERVICE_ADDR = os.environ.get("SENSOR_SERVICE_ADDR", "localhost:50052")


class SensorClient:
    def __init__(self, address: str = SENSOR_SERVICE_ADDR):
        self._channel = grpc.insecure_channel(address)
        self._sensor_service_stub = sensor_pb2_grpc.SensorServiceStub(self._channel)

        logger.info("Initialized GRPC sensor client")

    def get_reading(self, event_id: str) -> SensorReadingResponse:
        try:
            logger.info(f"Fetching sensor reading for event {event_id}")
            request = sensor_pb2.GetReadingRequest(event_id=event_id)

            grpc_response = self._sensor_service_stub.GetReading(request)
            logger.debug(f"GRPC Response for event {event_id}: {grpc_response}")
        except grpc.RpcError as exc:
            logger.error("GRPC Error while fetching reading for event %s: %s", event_id, exc)            
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise ValueError(f"Reading {event_id} not found") from exc
            raise

        response = SensorReadingResponse.from_proto(grpc_response)
        logger.info(f"Response for event {event_id}: {response}")

        return SensorReadingResponse.from_proto(response)

    def list_readings(self, limit: int = 10) -> list[SensorReadingResponse]:

        logger.info(f"Fetching list of sensor readings with limit {limit}")

        readingslist = self._sensor_service_stub.ListReadings(sensor_pb2.ListReadingsRequest(limit=limit))

        logger.debug(f"Retrieved list of sensor readings {readingslist}")

        return [SensorReadingResponse.from_proto(r) for r in readingslist]

    def close(self):
        self._channel.close()
