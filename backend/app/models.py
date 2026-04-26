from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class EmergencyRequest(BaseModel):
    user_id: str = Field(..., example="USR-001", description="Unique user identifier")
    name: str = Field(..., example="Priya Sharma", description="Person's name")
    latitude: float = Field(..., example=15.8281, description="GPS latitude")
    longitude: float = Field(..., example=78.0373, description="GPS longitude")
    location_label: Optional[str] = Field(None, example="Kurnool Bus Stand", description="Human-readable location")
    is_isolated: bool = Field(False, description="Is the person in an isolated area?")
    movement_status: str = Field("stationary", description="stationary | moving | erratic", example="stationary")
    time_of_day: Optional[str] = Field(None, description="Override time detection: morning|afternoon|evening|night")
    battery_level: Optional[int] = Field(None, ge=0, le=100, example=23, description="Device battery %")
    additional_context: Optional[str] = Field(None, example="Followed by unknown person", description="Any extra context")
    emergency_type: str = Field("general", description="general | medical | assault | accident | fire", example="general")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USR-001",
                "name": "Priya Sharma",
                "latitude": 15.8281,
                "longitude": 78.0373,
                "location_label": "Kurnool Bus Stand",
                "is_isolated": True,
                "movement_status": "stationary",
                "battery_level": 23,
                "additional_context": "Followed by unknown person for 10 minutes",
                "emergency_type": "general"
            }
        }


class EmergencyResponse(BaseModel):
    incident_id: str
    timestamp: str
    risk_score: int = Field(..., ge=0, le=100)
    severity: str
    risk_factors: List[str]
    ai_summary: str
    response_protocol: List[str]
    estimated_response_time: str
    status: str


class StatusResponse(BaseModel):
    status: str
    active_incidents: int
    total_incidents: int
    uptime_since: str
