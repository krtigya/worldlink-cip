"""
GET /api/changes         — recent change log
GET /api/changes/summary — counts by type this week
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter(prefix="/api/changes", tags=["Changes"])


@router.get("")
async def list_changes(
    severity:   Optional[str] = Query(None),
    change_type:Optional[str] = Query(None),
    isp:        Optional[str] = Query(None),
    days:       int           = Query(7, description="Look-back window in days"),
    limit:      int           = Query(100, le=500),
    db: AsyncSession          = Depends(get_db),
):
    q = """
        SELECT cl.*, i.name AS isp_name, i.slug AS isp_slug
        FROM change_logs cl
        JOIN isps i ON i.id = cl.isp_id
        WHERE cl.suppressed = false
          AND cl.detected_at >= NOW() - INTERVAL '1 day' * :days
    """
    params: dict = {"days": days, "limit": limit}

    if severity:    q += " AND cl.severity = :sev";       params["sev"]  = severity
    if change_type: q += " AND cl.change_type = :ctype";  params["ctype"]= change_type
    if isp:         q += " AND i.slug = :isp";            params["isp"]  = isp

    q += " ORDER BY cl.detected_at DESC LIMIT :limit"

    result = await db.execute(text(q), params)
    return {"data": [dict(r._mapping) for r in result.fetchall()]}


@router.get("/summary")
async def changes_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT change_type, severity, COUNT(*)::int AS count
        FROM change_logs
        WHERE detected_at >= NOW() - INTERVAL '7 days'
          AND suppressed = false
        GROUP BY change_type, severity
        ORDER BY count DESC
    """))
    return {"data": [dict(r._mapping) for r in result.fetchall()]}
