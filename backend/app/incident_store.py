import uuid
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models import EmergencyRequest


class IncidentStore:
    """
    In-memory incident store with optional JSON file persistence.
    On startup, loads existing incidents from disk if available.
    """

    STORAGE_FILE = "incidents.json"

    def __init__(self):
        self.start_time = datetime.utcnow().isoformat()
        self._incidents: Dict[str, Any] = {}
        self._load_from_disk()

    def save(self, req: EmergencyRequest, risk: Dict, summary: str) -> Dict:
        incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow().isoformat()

        incident = {
            "id": incident_id,
            "timestamp": timestamp,
            "status": "ACTIVE",
            "user": {
                "user_id": req.user_id,
                "name": req.name,
                "latitude": req.latitude,
                "longitude": req.longitude,
                "location_label": req.location_label,
                "battery_level": req.battery_level,
                "movement_status": req.movement_status,
                "is_isolated": req.is_isolated,
                "emergency_type": req.emergency_type,
                "additional_context": req.additional_context
            },
            "risk_score": risk["score"],
            "severity": risk["severity"],
            "risk_factors": risk["factors"],
            "ai_summary": summary,
            "response_protocol": risk["protocol"],
            "estimated_response_time": risk["eta"],
            "resolved_at": None
        }

        self._incidents[incident_id] = incident
        self._save_to_disk()
        return incident

    def get(self, incident_id: str) -> Optional[Dict]:
        return self._incidents.get(incident_id)

    def all(self) -> List[Dict]:
        return sorted(
            self._incidents.values(),
            key=lambda x: x["timestamp"],
            reverse=True
        )

    def resolve(self, incident_id: str) -> Optional[Dict]:
        if incident_id not in self._incidents:
            return None
        self._incidents[incident_id]["status"] = "RESOLVED"
        self._incidents[incident_id]["resolved_at"] = datetime.utcnow().isoformat()
        self._save_to_disk()
        return self._incidents[incident_id]

    def _save_to_disk(self):
        try:
            with open(self.STORAGE_FILE, "w") as f:
                json.dump(list(self._incidents.values()), f, indent=2)
        except Exception:
            pass  # Non-critical — in-memory always works

    def _load_from_disk(self):
        if not os.path.exists(self.STORAGE_FILE):
            return
        try:
            with open(self.STORAGE_FILE, "r") as f:
                data = json.load(f)
                for incident in data:
                    self._incidents[incident["id"]] = incident
        except Exception:
            pass
