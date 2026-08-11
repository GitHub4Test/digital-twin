"""
Data models and schemas for sensor data
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from uuid import uuid4, UUID

from google.protobuf.timestamp_pb2 import Timestamp

from api_gateway.generated.sensor.v1 import sensor_pb2


class SensorReading(BaseModel):
    """Request model for submitting a sensor reading"""

    event_id: str = Field(
        str(uuid4()),
        description="Unique Event UUID"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp when the reading was captured",
        examples=["2026-04-23T18:30:00Z"]
    )
    temperature: float = Field(
        ...,
        ge=-50,
        le=150,
        description="Temperature in Celsius",
        examples=[24.5]
    )
    humidity: float = Field(
        ...,
        ge=0,
        le=100,
        description="Relative humidity percentage",
        examples=[61.2]
    )

    @classmethod
    def from_proto(cls, proto_msg: sensor_pb2.SensorReading) -> "SensorReading":
        return cls(
            event_id=proto_msg.event_id,
            timestamp=proto_msg.timestamp.ToDatetime(tzinfo=timezone.utc),
            temperature=proto_msg.temperature,
            humidity=proto_msg.humidity,
        )

    def to_proto(self) -> sensor_pb2.SensorReading:
        ts = Timestamp()
        ts.FromDatetime(self.timestamp)
        return sensor_pb2.SensorReading(
            event_id=self.event_id,
            timestamp=ts,
            temperature=self.temperature,
            humidity=self.humidity,
        )

class SensorReadingResponse(BaseModel):
    event_id: str | None = Field(default=None, examples=["example-event-id"])
    timestamp: datetime = Field(examples=["2026-04-23T18:30:00Z"])
    temperature: float = Field(examples=[24.5])
    humidity: float = Field(examples=[61.2])
    status: str | None = Field(default=None, examples=["RECEIVED"])

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_proto(cls, proto_msg: sensor_pb2.SensorReadingResponse) -> "SensorReadingResponse":
        return cls(
            event_id=proto_msg.event_id, 
            timestamp=proto_msg.timestamp.ToDatetime(tzinfo=timezone.utc),
            temperature=proto_msg.temperature,
            humidity=proto_msg.humidity,
            status=proto_msg.status if hasattr(proto_msg, 'status') else None
        )

    def to_proto(self) -> sensor_pb2.SensorReadingResponse:
        ts = Timestamp()
        ts.FromDatetime(self.timestamp)
        return sensor_pb2.SensorReadingResponse(
            event_id=self.event_id,
            timestamp=ts,
            temperature=self.temperature,
            humidity=self.humidity,
            status=self.status if self.status is not None else ""
        )


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., examples=["healthy"])
    service: str = Field(..., examples=["backend"])
    version: str = Field(..., examples=["1.0.0"])

class MessageResponse(BaseModel):
    """Generic success response"""
    message: str = Field(..., examples=["Sensor reading stored successfully"])
    event_id: str | None = Field(default=None, examples=["example-event-id"])
    status: str | None = Field(default=None, examples=["RECEIVED"])

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., examples=["Database connection failed"])
