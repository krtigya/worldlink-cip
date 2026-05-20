"""
GET  /api/reports         — list past reports
GET  /api/reports/latest  — latest weekly report
POST /api/reports/generate — generate on-demand
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
