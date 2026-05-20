"""
POST /api/scrape/trigger — manually trigger scrape for one or all ISPs
GET  /api/scrape/runs    — recent scrape run history
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db, get_sync_db
from app.models import ScrapeRun
from app.ingestion.tasks.scrape_tasks import scrape_isp, scrape_all_isps

router = APIRouter(prefix="/api/scrape", tags=["Scraping"])


@router.post("/trigger")
async def trigger_scrape(isp_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Queue scrape job for one ISP (by isp_id) or all ISPs (no param)."""
    if isp_id:
        job    = scrape_isp.delay(isp_id)
        return {"message": f"Scrape queued for ISP {isp_id}", "job_id": job.id}
    else:
        result = scrape_all_isps.delay()
        return {"message": "All ISP scrapes queued", "job_id": result.id}


@router.get("/runs")
async def get_scrape_runs(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT sr.*, i.slug AS isp_slug, i.name AS isp_name
        FROM scrape_runs sr JOIN isps i ON i.id = sr.isp_id
        ORDER BY sr.started_at DESC LIMIT :limit
    """), {"limit": limit})
    return {"data": [dict(r._mapping) for r in result.fetchall()]}


@router.get("/runs/{run_id}")
async def get_scrape_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT sr.*, i.slug AS isp_slug, i.name AS isp_name
        FROM scrape_runs sr JOIN isps i ON i.id = sr.isp_id
        WHERE sr.id = :run_id
    """), {"run_id": run_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Scrape run not found")
    return {"data": dict(row._mapping)}
