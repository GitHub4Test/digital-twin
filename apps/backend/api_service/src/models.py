"""
Data models and schemas for sensor data
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SensorReadingCreate(BaseModel):
    """Request model for submitting a sensor reading"""
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

class SensorReadingResponse(BaseModel):
    timestamp: datetime = Field(examples=["2026-04-23T18:30:00Z"])
    temperature: float = Field(examples=[24.5])
    humidity: float = Field(examples=[61.2])

    model_config = ConfigDict(from_attributes=True)

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., examples=["healthy"])
    service: str = Field(..., examples=["backend"])
    version: str = Field(..., examples=["1.0.0"])

class MessageResponse(BaseModel):
    """Generic success response"""
    message: str = Field(..., examples=["Sensor reading stored successfully"])

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., examples=["Database connection failed"])
