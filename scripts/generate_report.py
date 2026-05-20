"""
app/reports/report_generator.py
Generates weekly competitive intelligence report using:
  - PostgreSQL queries for data aggregation
  - Groq LLM (llama-3.1-8b-instant) for executive summary + recommendations
"""
import json
from datetime import date, datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from groq import Groq
from app.config import get_settings
from app.models import WeeklyReport
from app.logger import get_logger

settings = get_settings()
logger   = get_logger(__name__)

SPEED_SEGMENTS = [25, 50, 100, 200, 300, 500, 1000]


class ReportGenerator:

    def __init__(self, session: Session):
        self.session = session
        self.groq    = Groq(api_key=settings.groq_api_key)

    async def generate(self, week_start: date) -> dict:
        week_end = week_start + timedelta(days=7)
        logger.info("report_start", week=str(week_start))

        cheapest_by_segment = self._get_cheapest_by_segment()
        new_campaigns       = self._get_new_campaigns(week_start, week_end)
        key_changes         = self._get_key_changes(week_start, week_end)
        market_overview     = self._get_market_overview()
        threats             = self._identify_threats(key_changes, cheapest_by_segment)
        recommendations     = await self._generate_recommendations(threats, key_changes)
        summary             = await self._generate_summary(key_changes, threats, cheapest_by_segment)

        report = {
            "report_week":         str(week_start),
            "generated_at":        datetime.utcnow().isoformat(),
            "summary":             summary,
            "cheapest_by_segment": cheapest_by_segment,
            "new_campaigns":       new_campaigns,
            "key_changes":         key_changes,
            "threats":             threats,
            "recommendations":     recommendations,
            "market_overview":     market_overview,
        }

        self._persist(week_start, summary, report)
        logger.info("report_complete", week=str(week_start))
        return report

    # -- Data queries -------------------------------------------------------

    def _get_cheapest_by_segment(self) -> list[dict]:
        results = []
        for mbps in SPEED_SEGMENTS:
            rows = self.session.execute(text("""
                SELECT i.name AS isp, p.normalized_name AS plan,
                       CAST(p.price_monthly AS FLOAT) AS price,
                       p.bundle_flags AS bundles
                FROM plans p
                JOIN isps i ON i.id = p.isp_id
                WHERE p.download_mbps = :mbps
                  AND p.status IN ('active','promotional')
                ORDER BY p.price_monthly ASC LIMIT 5
            """), {"mbps": mbps}).fetchall()

            if rows:
                results.append({
                    "segment": f"{mbps // 1000} Gbps" if mbps >= 1000 else f"{mbps} Mbps",
                    "plans": [
                        {"isp": r.isp, "plan": r.plan,
                         "price": r.price, "bundles": list(r.bundles or [])}
                        for r in rows
                    ],
                })
        return results

    def _get_new_campaigns(self, from_dt: date, to_dt: date) -> list[dict]:
        rows = self.session.execute(text("""
            SELECT c.title, c.description, c.campaign_type,
                   c.discount_pct, c.free_months,
                   c.valid_from, c.valid_to, i.name AS isp_name
            FROM campaigns c
            JOIN isps i ON i.id = c.isp_id
            WHERE c.first_seen_at::date BETWEEN :from_dt AND :to_dt
            ORDER BY c.first_seen_at DESC
        """), {"from_dt": from_dt, "to_dt": to_dt}).fetchall()

        return [
            {"isp": r.isp_name, "title": r.title, "description": r.description,
             "campaign_type": r.campaign_type, "discount_pct": float(r.discount_pct or 0),
             "free_months": r.free_months,
             "valid_from": str(r.valid_from), "valid_to": str(r.valid_to)}
            for r in rows
        ]

    def _get_key_changes(self, from_dt: date, to_dt: date) -> list[dict]:
        rows = self.session.execute(text("""
            SELECT cl.change_type, cl.severity, cl.summary,
                   cl.diff_pct, cl.details, cl.detected_at,
                   i.name AS isp_name
            FROM change_logs cl
            JOIN isps i ON i.id = cl.isp_id
            WHERE cl.detected_at::date BETWEEN :from_dt AND :to_dt
              AND cl.suppressed = false
              AND cl.severity IN ('high','critical')
            ORDER BY cl.detected_at DESC LIMIT 50
        """), {"from_dt": from_dt, "to_dt": to_dt}).fetchall()

        return [
            {"isp": r.isp_name, "change_type": r.change_type,
             "severity": r.severity, "summary": r.summary,
             "diff_pct": float(r.diff_pct) if r.diff_pct else None,
             "details": r.details, "detected_at": str(r.detected_at)}
            for r in rows
        ]

    def _get_market_overview(self) -> dict:
        rows = self.session.execute(text("""
            SELECT i.name AS isp_name, i.is_competitor,
                   COUNT(p.id)::int AS total_plans,
                   MIN(p.price_monthly)::float AS min_price,
                   MAX(p.price_monthly)::float AS max_price,
                   ROUND(AVG(p.price_monthly)::numeric, 0)::float AS avg_price,
                   MAX(p.download_mbps)::int AS max_speed,
                   COUNT(CASE WHEN 'iptv' = ANY(p.bundle_flags) THEN 1 END)::int AS plans_iptv,
                   COUNT(CASE WHEN 'ott'  = ANY(p.bundle_flags) THEN 1 END)::int AS plans_ott
            FROM plans p
            JOIN isps i ON i.id = p.isp_id
            WHERE p.status IN ('active','promotional')
            GROUP BY i.id, i.name, i.is_competitor
            ORDER BY total_plans DESC
        """)).fetchall()

        return {"isps": [dict(r._mapping) for r in rows]}

    # -- Threat identification ----------------------------------------------

    def _identify_threats(self, changes: list[dict], cheapest: list[dict]) -> list[dict]:
        threats = []

        for c in changes:
            if c["change_type"] == "price_decrease":
                threats.append({
                    "severity":          c["severity"],
                    "competitor":        c["isp"],
                    "description":       f"Price cut {abs(c.get('diff_pct') or 0):.1f}%: {c['summary']}",
                    "impacted_segments": [c["details"].get("download_mbps", "?")],
                    "recommended_action": "Review WorldLink pricing for this tier.",
                })
            elif c["change_type"] == "bundle_added":
                threats.append({
                    "severity":          "high",
                    "competitor":        c["isp"],
                    "description":       f"New bundle: {c['summary']}",
                    "impacted_segments": ["All residential"],
                    "recommended_action": "Evaluate OTT/streaming partnership.",
                })
            elif c["change_type"] == "speed_change":
                threats.append({
                    "severity":          c["severity"],
                    "competitor":        c["isp"],
                    "description":       f"Speed upgrade: {c['summary']}",
                    "impacted_segments": [str(c["details"].get("new_speed", "?")) + " Mbps"],
                    "recommended_action": "Review WorldLink speed tier equivalency.",
                })

        rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(threats, key=lambda t: rank.get(t["severity"], 9))

    # -- Groq LLM summarization ---------------------------------------------

    async def _generate_summary(
        self, changes: list, threats: list, cheapest: list
    ) -> str:
        context = {
            "total_changes":    len(changes),
            "critical_threats": sum(1 for t in threats if t["severity"] == "critical"),
            "price_drops":      sum(1 for c in changes if c["change_type"] == "price_decrease"),
            "new_plans":        sum(1 for c in changes if c["change_type"] == "plan_added"),
            "top_threats":      [t["description"] for t in threats[:3]],
        }
        try:
            resp = self.groq.chat.completions.create(
                model=settings.groq_llm_model,
                max_tokens=250,
                temperature=0.3,
                messages=[
                    {"role": "system",
                     "content": (
                         "You are a competitive intelligence analyst for WorldLink Communications "
                         "(Nepal ISP). Write a concise 3-4 sentence executive summary of the "
                         "week's competitive landscape. Be direct and business-focused."
                     )},
                    {"role": "user",
                     "content": f"Weekly data:\n{json.dumps(context, indent=2)}"},
                ],
            )
            return resp.choices[0].message.content or self._fallback_summary(changes, threats)
        except Exception as e:
            logger.warning("llm_summary_failed", error=str(e))
            return self._fallback_summary(changes, threats)

    async def _generate_recommendations(
        self, threats: list, changes: list
    ) -> list[str]:
        try:
            resp = self.groq.chat.completions.create(
                model=settings.groq_llm_model,
                max_tokens=400,
                temperature=0.4,
                messages=[
                    {"role": "system",
                     "content": (
                         "You are a competitive strategy consultant for WorldLink Communications "
                         "(Nepal ISP). Generate exactly 5 actionable recommendations as JSON. "
                         'Return ONLY: {"recommendations": ["...", ...]}'
                     )},
                    {"role": "user",
                     "content": json.dumps({"threats": threats[:5], "changes": len(changes)})},
                ],
            )
            text = resp.choices[0].message.content or "{}"
            text = text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            return parsed.get("recommendations", self._default_recommendations(threats))
        except Exception as e:
            logger.warning("llm_recommendations_failed", error=str(e))
            return self._default_recommendations(threats)

    def _fallback_summary(self, changes: list, threats: list) -> str:
        return (
            f"This week saw {len(changes)} competitive changes across Nepal ISP market. "
            f"{sum(1 for t in threats if t['severity'] == 'critical')} critical threats detected. "
            f"{sum(1 for c in changes if c['change_type'] == 'price_decrease')} competitor price "
            f"reductions require immediate attention."
        )

    def _default_recommendations(self, threats: list) -> list[str]:
        recs = [
            "Review pricing for speed tiers where competitors undercut WorldLink by >15%.",
            "Evaluate adding OTT bundle (Netflix/YouTube Premium) to flagship plans.",
            "Accelerate fiber rollout in areas where DishHome/Vianet are expanding.",
            "Consider loyalty discount to reduce churn risk from pricing pressure.",
            "Monitor Vianet and Subisu weekly for further promotional activity.",
        ]
        if any(t["severity"] == "critical" for t in threats):
            recs.insert(0, "URGENT: Critical threats detected. Schedule strategy review this week.")
        return recs

    # -- Persistence --------------------------------------------------------

    def _persist(self, week_start: date, summary: str, report: dict) -> None:
        existing = (
            self.session.query(WeeklyReport)
            .filter_by(report_week=week_start)
            .first()
        )
        if existing:
            existing.summary     = summary
            existing.full_report = report
            existing.generated_at = datetime.utcnow()
        else:
            self.session.add(WeeklyReport(
                report_week=week_start,
                summary=summary,
                full_report=report,
            ))
        self.session.commit()


# -- Sample report output ---------------------------------------------------

SAMPLE_REPORT_OUTPUT = {
    "report_week": "2025-06-02",
    "summary": (
        "This week, Vianet aggressively cut 300 Mbps pricing by 25%, posing a critical threat "
        "to WorldLink's mid-tier residential segment. DishHome launched two new IPTV bundle plans "
        "while Subisu added YouTube Premium to all plans >= 200 Mbps. WorldLink holds a competitive "
        "edge at 500 Mbps+ enterprise but requires urgent response in mass-market tiers."
    ),
    "threats": [
        {
            "severity":          "critical",
            "competitor":        "Vianet",
            "description":       "Price cut 25.0%: Vianet 300 Mbps dropped NPR 1,999 to 1,499",
            "impacted_segments": ["300 Mbps"],
            "recommended_action": "Immediate: Match pricing or launch competing promotional offer within 2 weeks.",
        },
        {
            "severity":          "high",
            "competitor":        "Subisu",
            "description":       "New bundle: Subisu added YouTube Premium to all >= 200 Mbps plans",
            "impacted_segments": ["All residential"],
            "recommended_action": "Negotiate OTT partnership to maintain bundle parity.",
        },
    ],
    "recommendations": [
        "URGENT: Match Vianet 300 Mbps pricing or introduce a competitive promo within 2 weeks.",
        "Partner with Netflix/YouTube Premium for mid-tier plan bundle (200-500 Mbps).",
        "Launch 'loyalty lock' promo: 6-month price guarantee for existing customers.",
        "Accelerate fiber deployment in Lalitpur/Bhaktapur where DishHome is expanding.",
        "Introduce 15% annual prepay discount to improve retention and cash flow.",
    ],
}
