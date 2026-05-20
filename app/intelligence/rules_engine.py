"""
app/intelligence/rules_engine.py
Evaluates change events against configurable alert rules.
Rules are stored in DB and loaded at startup.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import IntelRule, Plan, SeverityLevel
from app.detection.change_detector import ChangeEvent, ChangeType
from app.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AlertPayload:
    rule_key: str
    severity: SeverityLevel
    isp_name: str
    change_type: str
    summary: str
    details: dict
    plan: Optional[dict]
    detected_at: datetime


class RulesEngine:

    def __init__(self, session: Session):
        self.session = session
        self._rules: list[IntelRule] = []

    def load_rules(self) -> None:
        self._rules = (
            self.session.query(IntelRule)
            .filter_by(is_enabled=True)
            .all()
        )
        logger.info("rules_loaded", count=len(self._rules))

    def evaluate(
        self,
        events: list[ChangeEvent],
        plans_by_id: dict[str, Plan],
        isp_names: dict[int, str],
    ) -> list[AlertPayload]:
        if not self._rules:
            self.load_rules()

        alerts: list[AlertPayload] = []

        for event in events:
            for rule in self._rules:
                if not self._matches(event, rule.condition, plans_by_id):
                    continue
                if not self._passes_cooldown(rule):
                    continue
                if rule.condition.get("type") == "price_diff":
                    if not self._check_vs_worldlink(event):
                        continue

                plan   = plans_by_id.get(event.plan_id) if event.plan_id else None
                alerts.append(AlertPayload(
                    rule_key=rule.rule_key,
                    severity=rule.severity,
                    isp_name=isp_names.get(event.isp_id, f"ISP#{event.isp_id}"),
                    change_type=event.change_type.value,
                    summary=event.summary,
                    details={**event.details, "rule_name": rule.name},
                    plan={"normalized_name": plan.normalized_name,
                          "download_mbps": plan.download_mbps,
                          "price_monthly": float(plan.price_monthly),
                          "bundle_flags": plan.bundle_flags} if plan else None,
                    detected_at=datetime.now(timezone.utc),
                ))
                self._bump_trigger(rule)

        return alerts

    # ── Condition matching ─────────────────────────────────────────────────

    def _matches(self, event: ChangeEvent, condition: dict, plans: dict) -> bool:
        ctype = condition.get("type")

        if ctype == "change_type":
            return event.change_type.value == condition["value"]

        if ctype == "price_diff":
            if event.diff_pct is None:
                return False
            return self._compare(event.diff_pct, condition["operator"], condition["threshold"])

        if ctype == "compound":
            return all(self._matches(event, c, plans) for c in condition["conditions"])

        return False

    def _compare(self, value: float, operator: str, threshold: float) -> bool:
        ops = {"lt": value < threshold, "gt": value > threshold,
               "lte": value <= threshold, "gte": value >= threshold,
               "eq": abs(value - threshold) < 0.5}
        return ops.get(operator, False)

    def _passes_cooldown(self, rule: IntelRule) -> bool:
        if not rule.last_triggered:
            return True
        elapsed_hours = (datetime.now(timezone.utc) - rule.last_triggered).total_seconds() / 3600
        return elapsed_hours >= rule.cooldown_hours

    def _check_vs_worldlink(self, event: ChangeEvent) -> bool:
        """Check price diff against WorldLink equivalent in DB."""
        if not event.plan_id:
            return False
        row = self.session.execute(
            text("""
                SELECT ROUND(((p.price_monthly - wl.price_monthly) / wl.price_monthly) * 100, 1) AS diff_pct
                FROM plans p
                JOIN isps i ON i.id = p.isp_id
                CROSS JOIN LATERAL (
                    SELECT price_monthly FROM plans wp
                    JOIN isps wi ON wi.id = wp.isp_id
                    WHERE wi.is_competitor = false AND wp.download_mbps = p.download_mbps
                    AND wp.status = 'active' LIMIT 1
                ) wl
                WHERE p.id = :plan_id AND i.is_competitor = true
            """),
            {"plan_id": event.plan_id}
        ).fetchone()
        return row is not None and row.diff_pct is not None

    def _bump_trigger(self, rule: IntelRule) -> None:
        rule.last_triggered = datetime.now(timezone.utc)
        rule.trigger_count  = (rule.trigger_count or 0) + 1
        self.session.commit()
