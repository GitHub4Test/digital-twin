"""
Events for sensor data readings and processing
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SensorReadingEvent(BaseModel):
    event_id: UUID
    event_type: str = Field(default="sensor.reading.received")
    source: str = Field(default="api-gateway")
    timestamp: datetime
    temperature: float
    humidity: float
