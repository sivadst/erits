from datetime import datetime
from app.models import EmergencyRequest
from typing import Dict, Any


class AlertEngine:
    """
    Intelligent alert summary generator.
    Uses structured template logic with contextual branching to produce
    human-readable, actionable emergency summaries — no external AI API required.
    """

    SEVERITY_OPENERS = {
        "CRITICAL": [
            "🚨 CRITICAL ALERT: Immediate intervention required.",
            "🔴 PRIORITY ONE EMERGENCY: All units respond.",
            "🚨 URGENT: Life-threatening situation detected."
        ],
        "HIGH": [
            "🟠 HIGH PRIORITY: Rapid response needed.",
            "⚠️ ELEVATED THREAT: Emergency team on standby.",
            "🟠 HIGH ALERT: Situation requires swift action."
        ],
        "MODERATE": [
            "🟡 MODERATE CONCERN: Monitor and verify status.",
            "⚠️ CAUTION: Potential emergency in progress.",
            "🟡 ALERT: Situation flagged for review."
        ],
        "LOW": [
            "🟢 LOW RISK: Precautionary alert logged.",
            "ℹ️ NOTICE: Emergency signal received and logged.",
            "🟢 MONITORING: Situation under passive observation."
        ]
    }

    EMERGENCY_DESCRIPTIONS = {
        "assault": "a potential assault situation",
        "medical": "a medical emergency",
        "fire": "a fire or smoke emergency",
        "accident": "an accident or collision",
        "general": "an emergency situation"
    }

    def generate_summary(self, req: EmergencyRequest, risk: Dict[str, Any]) -> str:
        now = datetime.now()
        time_label = self._get_time_label(now.hour)
        location = req.location_label or f"coordinates ({req.latitude:.4f}, {req.longitude:.4f})"
        severity = risk["severity"]
        score = risk["score"]
        emergency_desc = self.EMERGENCY_DESCRIPTIONS.get(req.emergency_type, "an emergency")

        # Pick opener based on severity (deterministic rotation using score)
        openers = self.SEVERITY_OPENERS[severity]
        opener = openers[score % len(openers)]

        # Build context sentence
        context_parts = []
        if req.is_isolated:
            context_parts.append("is in an isolated area")
        if req.movement_status == "erratic":
            context_parts.append("is showing erratic movement")
        elif req.movement_status == "stationary":
            context_parts.append("has been stationary")
        if req.battery_level is not None and req.battery_level < 20:
            context_parts.append(f"has critical battery at {req.battery_level}%")

        context_sentence = ""
        if context_parts:
            context_sentence = f" The individual {', and '.join(context_parts)}."

        # User context
        user_context_sentence = ""
        if req.additional_context:
            user_context_sentence = f' Reported context: "{req.additional_context}"'

        # Build the summary
        summary = (
            f"{opener}\n\n"
            f"Individual: {req.name} (ID: {req.user_id}) has triggered {emergency_desc} "
            f"at {location} during {time_label} hours.{context_sentence}"
            f"{user_context_sentence}\n\n"
            f"Risk Assessment: Score {score}/100 — {severity} severity. "
            f"{self._get_risk_narrative(score, severity)}\n\n"
            f"Estimated Response Time: {risk['eta']}. "
            f"{self._get_closing_instruction(severity)}"
        )

        return summary

    def _get_time_label(self, hour: int) -> str:
        if hour < 5:
            return "late night"
        elif hour < 9:
            return "early morning"
        elif hour < 12:
            return "morning"
        elif hour < 17:
            return "afternoon"
        elif hour < 20:
            return "evening"
        return "night"

    def _get_risk_narrative(self, score: int, severity: str) -> str:
        if severity == "CRITICAL":
            return (
                "Multiple compounding risk factors identified. "
                "Probability of serious harm is high without immediate intervention."
            )
        elif severity == "HIGH":
            return (
                "Significant risk indicators present. "
                "Situation may deteriorate rapidly — early response is critical."
            )
        elif severity == "MODERATE":
            return (
                "Moderate risk factors detected. "
                "User should be contacted immediately to verify safety."
            )
        return (
            "Minimal immediate risk indicators. "
            "Standard monitoring protocols have been activated."
        )

    def _get_closing_instruction(self, severity: str) -> str:
        instructions = {
            "CRITICAL": (
                "All emergency contacts have been notified. "
                "Do NOT delay response. Treat as life-threatening until confirmed otherwise."
            ),
            "HIGH": (
                "Primary emergency contacts have been alerted. "
                "Response team should proceed to location with caution."
            ),
            "MODERATE": (
                "A check-in notification has been sent to the user. "
                "Escalate to HIGH if no response within 5 minutes."
            ),
            "LOW": (
                "Incident has been logged. "
                "Automated follow-up will be sent in 15 minutes."
            )
        }
        return instructions.get(severity, "")
