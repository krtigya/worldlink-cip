"""
GET  /api/reports            — list past reports
GET  /api/reports/latest     — latest weekly report
GET  /api/reports/positioning — WorldLink position vs competitors at each speed tier
POST /api/reports/generate   — generate on-demand
"""
from datetime import date, timedelta
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db, get_sync_db
from app.reports.report_generator import ReportGenerator

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("")
async def list_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT id, report_week, summary, generated_at, sent_at
        FROM weekly_reports ORDER BY report_week DESC LIMIT 20
    """))
    return {"data": [dict(r._mapping) for r in result.fetchall()]}


@router.get("/latest")
async def get_latest_report(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text(
        "SELECT * FROM weekly_reports ORDER BY report_week DESC LIMIT 1"
    ))
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No reports generated yet")
    return {"data": dict(row._mapping)}


@router.get("/positioning")
async def market_positioning(db: AsyncSession = Depends(get_db)):
    """WorldLink price position vs competitors at each speed tier."""
    result = await db.execute(text("""
        WITH wl AS (
            SELECT download_mbps, MIN(price_monthly) AS wl_price
            FROM plans
            JOIN isps ON isps.id = plans.isp_id
            WHERE isps.is_competitor = false AND plans.status = 'active'
            GROUP BY download_mbps
        ),
        comp AS (
            SELECT i.name AS isp_name, p.download_mbps,
                   MIN(p.price_monthly) AS cheapest_price
            FROM plans p
            JOIN isps i ON i.id = p.isp_id
            WHERE i.is_competitor = true AND p.status = 'active'
            GROUP BY i.name, p.download_mbps
        )
        SELECT comp.isp_name, comp.download_mbps,
               comp.cheapest_price AS competitor_cheapest,
               wl.wl_price AS worldlink_price,
               CASE
                   WHEN wl.wl_price IS NULL THEN 'no_worldlink_plan'
                   WHEN comp.cheapest_price < wl.wl_price THEN 'competitor_cheaper'
                   WHEN comp.cheapest_price > wl.wl_price THEN 'worldlink_cheaper'
                   ELSE 'same_price'
               END AS position,
               CASE WHEN wl.wl_price IS NOT NULL
                   THEN ROUND(((comp.cheapest_price - wl.wl_price) / wl.wl_price * 100)::numeric, 1)
               END AS diff_pct
        FROM comp
        LEFT JOIN wl ON wl.download_mbps = comp.download_mbps
        ORDER BY comp.download_mbps, comp.isp_name
    """))
    rows = [dict(r._mapping) for r in result.fetchall()]

    worldlink_cheaper  = sum(1 for r in rows if r["position"] == "worldlink_cheaper")
    competitor_cheaper = sum(1 for r in rows if r["position"] == "competitor_cheaper")
    no_coverage        = sum(1 for r in rows if r["position"] == "no_worldlink_plan")

    return {
        "data": rows,
        "summary": {
            "worldlink_cheaper_count":    worldlink_cheaper,
            "competitor_cheaper_count":   competitor_cheaper,
            "no_worldlink_coverage_count": no_coverage,
            "worldlink_advantage_pct":    round(worldlink_cheaper / len(rows) * 100, 1) if rows else 0,
        },
    }


@router.post("/generate")
async def generate_report():
    """Trigger on-demand report generation for current week."""
    try:
        session    = next(get_sync_db())
        today      = date.today()
        week_start = today - timedelta(days=today.weekday())
        generator  = ReportGenerator(session)
        report     = await generator.generate(week_start)
        return {"message": "Report generated", "week": str(week_start),
                "summary": report.get("summary", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))