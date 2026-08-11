"""
Events for sensor data readings and processing
"""

from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class SensorReadingEvent(BaseModel):
    event_id: UUID
    event_type: str = Field(default="sensor.reading.received")
    source: str = Field(default="api-gateway")
    timestamp: datetime
    temperature: float
    humidity: float