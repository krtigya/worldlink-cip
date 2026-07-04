"""
here I write the code for alert_dispatcher.py
app/alerts/alert_dispatcher.py
Dispatches alerts to Slack (webhook) and email (HTML).
Builds rich Slack Block Kit messages with color-coded severity.
"""
import httpx
from datetime import datetime
from jinja2 import Template
from app.config import get_settings
from app.intelligence.rules_engine import AlertPayload
from app.logger import get_logger

settings = get_settings()
logger   = get_logger(__name__)

SEVERITY_EMOJI = {
    "critical": "🚨",
    "high":     "⚠️",
    "medium":   "ℹ️",
    "low":      "🆗",
}

SEVERITY_COLOR = {
    "critical": "#FF0000",
    "high":     "#FF6B00",
    "medium":   "#FFC107",
    "low":      "#2196F3",
}

SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class AlertDispatcher:

    async def dispatch(self, alerts: list[AlertPayload]) -> None:
        if not alerts:
            return

        slack_alerts = alerts
        email_alerts = [a for a in alerts if a.severity in ("critical", "high")]

        import asyncio
        await asyncio.gather(
            self._send_slack(slack_alerts),
            self._send_email(email_alerts),
            return_exceptions=True,
        )

    async def _send_slack(self, alerts: list[AlertPayload]) -> None:
        webhook = get_settings().slack_webhook_url
        if not alerts or not webhook:
            return

        for batch in _chunk(alerts, 20):
            payload = self._build_slack_payload(batch)
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.post(webhook, json=payload)
                    resp.raise_for_status()
                logger.info("slack_sent", count=len(batch))
            except Exception as e:
                logger.error("slack_dispatch_failed", error=str(e))

    def _build_slack_payload(self, alerts: list[AlertPayload]) -> dict:
        top_sev = max(alerts, key=lambda a: SEVERITY_RANK[a.severity]).severity
        blocks  = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{SEVERITY_EMOJI[top_sev]} CIP Alert — {len(alerts)} change(s) detected",
                    "emoji": True,
                },
            },
            {"type": "divider"},
        ]

        for alert in alerts[:15]:
            fields = []
            if alert.plan:
                fields += [
                    {"type": "mrkdwn", "text": f"*Speed:* {alert.plan['download_mbps']} Mbps"},
                    {"type": "mrkdwn", "text": f"*Price:* NPR {alert.plan['price_monthly']}/mo"},
                ]
            if alert.details.get("diff_pct") is not None:
                diff = float(alert.details["diff_pct"])
                fields.append({"type": "mrkdwn", "text": f"*Change:* {diff:+.1f}%"})

            block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{SEVERITY_EMOJI[alert.severity]} [{alert.severity.upper()}]* "
                        f"— *{alert.isp_name}*\n{alert.summary}"
                    ),
                },
            }
            if fields:
                block["fields"] = fields
            blocks.append(block)

        if len(alerts) > 15:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn",
                         "text": f"_…and {len(alerts) - 15} more. Check the CIP dashboard._"},
            })

        blocks.append({
            "type": "context",
            "elements": [{"type": "mrkdwn",
                          "text": f"Detected {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | WorldLink CIP"}],
        })

        return {
            "text": f"CIP: {len(alerts)} competitive change(s) detected",
            "attachments": [{"color": SEVERITY_COLOR[top_sev], "blocks": blocks}],
        }


    async def _send_email(self, alerts: list[AlertPayload]) -> None:
        if not alerts:
            return
        cfg     = get_settings()
        subject = (
            f"[CIP Alert] {len(alerts)} change(s) — "
            f"{'🚨 CRITICAL' if any(a.severity == 'critical' for a in alerts) else '⚠️ HIGH'}"
        )
        html = self._build_email_html(alerts)
        # Log for now — swap in smtplib / SendGrid / SES for production
        logger.info("email_alert_generated", to=cfg.alert_email,
                    subject=subject, alert_count=len(alerts))

    def _build_email_html(self, alerts: list[AlertPayload]) -> str:
        template = Template("""
        <html><body style="font-family:sans-serif;max-width:900px;margin:auto">
          <h2>🌐 WorldLink CIP — Competitive Alert</h2>
          <p><strong>{{ alerts|length }} change(s)</strong> detected at {{ now }}</p>
          <table style="width:100%;border-collapse:collapse;font-size:14px">
            <thead>
              <tr style="background:#1a1a2e;color:white">
                <th style="padding:10px">Severity</th>
                <th style="padding:10px">Competitor</th>
                <th style="padding:10px">Summary</th>
                <th style="padding:10px">Time</th>
              </tr>
            </thead>
            <tbody>
              {% for a in alerts %}
              <tr style="border-bottom:1px solid #eee">
                <td style="padding:8px">{{ emoji[a.severity] }} {{ a.severity }}</td>
                <td style="padding:8px"><strong>{{ a.isp_name }}</strong></td>
                <td style="padding:8px">{{ a.summary }}</td>
                <td style="padding:8px">{{ a.detected_at.strftime('%Y-%m-%d %H:%M') }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          <p style="color:#888;font-size:12px;margin-top:20px">
            WorldLink Communications Internal CIP — Confidential
          </p>
        </body></html>
        """)
        return template.render(
            alerts=alerts,
            now=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            emoji=SEVERITY_EMOJI,
        )


def _chunk(lst, size):
    return [lst[i:i+size] for i in range(0, len(lst), size)]




SAMPLE_SLACK_OUTPUT = {
    "text": "CIP: 2 competitive change(s) detected",
    "attachments": [{
        "color": "#FF0000",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text",
                         "text": "🚨 CIP Alert — 2 change(s) detected"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "*🚨 [CRITICAL]* — *Vianet Communications*\n"
                        "Vianet 300 Mbps: price dropped NPR 1,999 → 1,499 (-25.0%)"
                    )
                },
                "fields": [
                    {"type": "mrkdwn", "text": "*Speed:* 300 Mbps"},
                    {"type": "mrkdwn", "text": "*Price:* NPR 1,499/mo"},
                    {"type": "mrkdwn", "text": "*Change:* -25.0%"},
                ],
            },
        ],
    }],
}