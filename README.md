# 🚨 ERITS — Emergency Response & Intelligent Tracking System

A production-ready, real-time emergency response system with AI-powered risk scoring, alert generation, and a polished one-click UI.

---

## ⚡ Quick Start (3 steps)

### 1. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the server
```bash
uvicorn app.main:app --reload
```

### 3. Open the app
Visit: **http://localhost:8000**

The API docs are at: **http://localhost:8000/docs**

---

## 📁 Project Structure

```
emergency_system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           ← FastAPI app + routes
│   │   ├── models.py         ← Pydantic request/response models
│   │   ├── risk_engine.py    ← Risk scoring logic (0–100)
│   │   ├── alert_engine.py   ← AI-style summary generator
│   │   └── incident_store.py ← In-memory + JSON persistence
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── index.html            ← Full-featured emergency dashboard
└── README.md
```

---

## 🎯 Core Features

| Feature | Description |
|---|---|
| **Panic Button** | One-click emergency trigger with animated UI |
| **Risk Scoring** | 0–100 score based on time, isolation, movement, battery, context |
| **AI Summary** | Structured, context-aware alert summary (no external API) |
| **Response Protocol** | Severity-matched response steps |
| **Incident Log** | Live log with resolve functionality |
| **JSON Persistence** | Incidents saved to `incidents.json` on disk |
| **REST API** | Full CRUD via FastAPI with auto-generated Swagger docs |

---

## 🌐 API Endpoints

### POST /api/emergency
Trigger an emergency alert.

**Sample cURL:**
```bash
curl -X POST http://localhost:8000/api/emergency \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR-001",
    "name": "Priya Sharma",
    "latitude": 15.8281,
    "longitude": 78.0373,
    "location_label": "Kurnool Bus Stand",
    "is_isolated": true,
    "movement_status": "stationary",
    "battery_level": 15,
    "additional_context": "Being followed by unknown person",
    "emergency_type": "assault"
  }'
```

**Sample Response:**
```json
{
  "incident_id": "INC-A3F8C102",
  "timestamp": "2025-04-26T14:32:01.123456",
  "risk_score": 86,
  "severity": "CRITICAL",
  "risk_factors": [
    "Emergency type: ASSAULT (+40 pts)",
    "Night-time incident — heightened vulnerability (+18 pts)",
    "Isolated location detected (+20 pts)",
    "Person stationary — possible incapacitation (+5 pts)"
  ],
  "ai_summary": "🚨 CRITICAL ALERT: Immediate intervention required...",
  "response_protocol": [
    "🚨 Dispatch nearest emergency unit immediately",
    "📞 Auto-dial emergency contacts",
    ...
  ],
  "estimated_response_time": "4–7 minutes",
  "status": "ACTIVE"
}
```

### GET /api/incidents
Returns all incidents, newest first.

### GET /api/incidents/{incident_id}
Fetch a specific incident.

### POST /api/incidents/{incident_id}/resolve
Mark an incident as resolved.

### GET /api/status
System health check with active/total incident counts.

---

## 🧠 Risk Scoring Logic

The `RiskEngine` evaluates multiple weighted factors:

| Factor | Max Score |
|---|---|
| Emergency Type (assault/medical/fire) | +40 pts |
| Night-time (10pm–5am) | +18 pts |
| Isolated location | +20 pts |
| Erratic movement | +15 pts |
| Low battery (<20%) | +8 pts |
| Danger keywords in context | +15 pts |

**Severity Thresholds:**
- 🔴 CRITICAL: 80–100
- 🟠 HIGH: 60–79
- 🟡 MODERATE: 40–59
- 🟢 LOW: 0–39

---

## 🛠️ Tech Stack

- **Backend:** FastAPI + Pydantic v2 + Uvicorn
- **Frontend:** Pure HTML/CSS/JS (zero dependencies, no build step)
- **Persistence:** In-memory dict + JSON file
- **Fonts:** Syne + JetBrains Mono (Google Fonts CDN)

---

## 🚀 Hackathon Extensions

Ideas to extend this into a full product:
- Add WebSockets for real-time incident push to dashboards
- Integrate Twilio for actual SMS alerts
- Add Google Maps embed for live GPS tracking
- Connect to a real AI API (Claude/GPT) for richer summaries
- Add user authentication with JWT
- Deploy to Railway/Render with a single `railway up`
