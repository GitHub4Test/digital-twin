import os
import grpc

from api_gateway.generated.sensor.v1 import sensor_pb2, sensor_pb2_grpc

SENSOR_SERVICE_ADDR = os.environ.get("SENSOR_SERVICE_ADDR", "localhost:50052")

class SensorClient:
    def __init__(self, address: str = SENSOR_SERVICE_ADDR):
        self._channel = grpc.insecure_channel(address)
        self._sensorServiceStub = sensor_pb2_grpc.SensorServiceStub(self._channel)

    def getReading(self, event_id: str) -> SensorReadingResponse:

        try:
            request = sensor_pb2.GetReadingRequest(event_id=event_id)
            response = self._sensorServiceStub.GetReading(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise ValueError(f"Reading {event_id} not found") from e
            raise            
        return SensorReadingResponse.from_proto(response)

    def listReadings(self, limit: int = 10) -> list[SensorReadingResponse]:

        request = self._sensorServiceStub.ListReadings(sensor_pb2.ListReadingsRequest(limit=limit))

        return [SensorReadingResponse.from_proto(r) for r in request]

    def close(self):
        self._channel.close()
    