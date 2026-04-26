from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import os

from app.models import EmergencyRequest, EmergencyResponse, StatusResponse
from app.risk_engine import RiskEngine
from app.alert_engine import AlertEngine
from app.incident_store import IncidentStore

app = FastAPI(
    title="Emergency Response & Intelligent Tracking System",
    description="Real-time emergency response with AI-powered risk scoring and alert generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

risk_engine = RiskEngine()
alert_engine = AlertEngine()
incident_store = IncidentStore()

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Emergency Response API is running. Visit /docs for API reference."}


@app.post("/api/emergency", response_model=EmergencyResponse)
async def trigger_emergency(request: EmergencyRequest):
    """
    Trigger an emergency alert. Accepts location, user context, and environmental signals.
    Returns a risk score, severity classification, AI-generated summary, and response protocol.
    """
    risk_result = risk_engine.evaluate(request)
    summary = alert_engine.generate_summary(request, risk_result)
    incident = incident_store.save(request, risk_result, summary)

    return EmergencyResponse(
        incident_id=incident["id"],
        timestamp=incident["timestamp"],
        risk_score=risk_result["score"],
        severity=risk_result["severity"],
        risk_factors=risk_result["factors"],
        ai_summary=summary,
        response_protocol=risk_result["protocol"],
        estimated_response_time=risk_result["eta"],
        status="ACTIVE"
    )


@app.get("/api/incidents", response_model=list)
async def list_incidents():
    """Return all logged incidents (most recent first)."""
    return incident_store.all()


@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Fetch a specific incident by ID."""
    incident = incident_store.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.post("/api/incidents/{incident_id}/resolve")
async def resolve_incident(incident_id: str):
    """Mark an incident as resolved."""
    incident = incident_store.resolve(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"status": "RESOLVED", "incident_id": incident_id, "resolved_at": datetime.utcnow().isoformat()}


@app.get("/api/status", response_model=StatusResponse)
async def system_status():
    """Health check and live system statistics."""
    incidents = incident_store.all()
    active = [i for i in incidents if i.get("status") == "ACTIVE"]
    return StatusResponse(
        status="OPERATIONAL",
        active_incidents=len(active),
        total_incidents=len(incidents),
        uptime_since=incident_store.start_time
    )
