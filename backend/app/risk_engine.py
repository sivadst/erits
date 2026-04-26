from datetime import datetime
from app.models import EmergencyRequest
from typing import Dict, Any


class RiskEngine:
    """
    Deterministic risk scoring engine.
    Evaluates: time of day, isolation, movement, emergency type, battery, and context signals.
    Outputs a 0–100 risk score with severity classification and response protocol.
    """

    SEVERITY_THRESHOLDS = {
        "CRITICAL": 80,
        "HIGH": 60,
        "MODERATE": 40,
        "LOW": 0
    }

    EMERGENCY_BASE_SCORES = {
        "assault": 40,
        "medical": 35,
        "fire": 38,
        "accident": 30,
        "general": 15
    }

    RESPONSE_PROTOCOLS = {
        "CRITICAL": [
            "🚨 Dispatch nearest emergency unit immediately",
            "📞 Auto-dial emergency contacts",
            "📍 Share live GPS with responders",
            "🔊 Activate silent alarm on device",
            "👮 Notify local law enforcement"
        ],
        "HIGH": [
            "🚑 Alert nearest response team",
            "📞 Notify primary emergency contact",
            "📍 Enable continuous location tracking",
            "💬 Send automated SOS to 3 contacts"
        ],
        "MODERATE": [
            "📞 Contact user to confirm status",
            "📍 Begin location monitoring",
            "💬 Send check-in notification",
            "⏱️ Escalate if no response in 5 minutes"
        ],
        "LOW": [
            "📋 Log incident for monitoring",
            "💬 Send reassurance notification to user",
            "📍 Passive location tracking enabled"
        ]
    }

    ETA_MAP = {
        "CRITICAL": "4–7 minutes",
        "HIGH": "7–12 minutes",
        "MODERATE": "12–20 minutes",
        "LOW": "20–30 minutes"
    }

    DANGER_KEYWORDS = [
        "follow", "threat", "attack", "help", "danger", "hurt",
        "bleed", "fire", "crash", "weapon", "knife", "gun",
        "unconscious", "faint", "pain", "trap", "alone", "dark"
    ]

    def evaluate(self, req: EmergencyRequest) -> Dict[str, Any]:
        score = 0
        factors = []

        # Base score from emergency type
        base = self.EMERGENCY_BASE_SCORES.get(req.emergency_type, 15)
        score += base
        if req.emergency_type != "general":
            factors.append(f"Emergency type: {req.emergency_type.upper()} (+{base} pts)")

        # Time of day risk
        time_score, time_factor = self._evaluate_time(req.time_of_day)
        score += time_score
        if time_factor:
            factors.append(time_factor)

        # Isolation risk
        if req.is_isolated:
            score += 20
            factors.append("Isolated location detected (+20 pts)")

        # Movement risk
        move_score, move_factor = self._evaluate_movement(req.movement_status)
        score += move_score
        if move_factor:
            factors.append(move_factor)

        # Battery risk
        if req.battery_level is not None and req.battery_level < 20:
            score += 8
            factors.append(f"Low battery: {req.battery_level}% — risk of signal loss (+8 pts)")

        # Context keyword analysis
        ctx_score, ctx_factor = self._evaluate_context(req.additional_context)
        score += ctx_score
        if ctx_factor:
            factors.append(ctx_factor)

        # Cap at 100
        score = min(score, 100)

        severity = self._classify_severity(score)

        return {
            "score": score,
            "severity": severity,
            "factors": factors if factors else ["Standard emergency signal received"],
            "protocol": self.RESPONSE_PROTOCOLS[severity],
            "eta": self.ETA_MAP[severity]
        }

    def _evaluate_time(self, time_override: str | None):
        now_hour = datetime.now().hour
        if time_override:
            mapping = {"morning": 8, "afternoon": 14, "evening": 19, "night": 23}
            now_hour = mapping.get(time_override, now_hour)

        if 22 <= now_hour or now_hour < 5:
            return 18, "Night-time incident — heightened vulnerability (+18 pts)"
        elif 5 <= now_hour < 7:
            return 10, "Pre-dawn hours — low visibility risk (+10 pts)"
        elif 18 <= now_hour < 22:
            return 8, "Evening hours — elevated risk window (+8 pts)"
        return 0, ""

    def _evaluate_movement(self, movement: str):
        if movement == "erratic":
            return 15, "Erratic movement pattern — possible distress signal (+15 pts)"
        elif movement == "stationary":
            return 5, "Person stationary — possible incapacitation (+5 pts)"
        return 0, ""

    def _evaluate_context(self, context: str | None):
        if not context:
            return 0, ""
        context_lower = context.lower()
        matched = [kw for kw in self.DANGER_KEYWORDS if kw in context_lower]
        if len(matched) >= 3:
            return 15, f"High-danger keywords in context: {', '.join(matched[:3])} (+15 pts)"
        elif len(matched) >= 1:
            return 8, f"Threat keywords detected: {', '.join(matched)} (+8 pts)"
        return 2, "Additional context provided (+2 pts)"

    def _classify_severity(self, score: int) -> str:
        for level, threshold in self.SEVERITY_THRESHOLDS.items():
            if score >= threshold:
                return level
        return "LOW"
