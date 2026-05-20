"""
GET /api/plans          — list active plans with filters
GET /api/plans/compare  — WorldLink vs competitors at same speed
GET /api/plans/{id}     — single plan detail
GET /api/plans/{id}/history — pricing history
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.db.session import get_db
from app.models import Plan, PricingHistory
from app.schemas.plan import PlanResponse, PlanListResponse, PricingHistoryResponse

router = APIRouter(prefix="/api/plans", tags=["Plans"])


@router.get("", response_model=PlanListResponse)
async def list_plans(
    isp:       Optional[str]   = Query(None, description="Filter by ISP slug"),
    min_speed: Optional[int]   = Query(None, description="Min download Mbps"),
    max_speed: Optional[int]   = Query(None, description="Max download Mbps"),
    max_price: Optional[float] = Query(None, description="Max monthly price NPR"),
    bundle:    Optional[str]   = Query(None, description="Bundle flag e.g. iptv, ott, router"),
    plan_type: Optional[str]   = Query(None, description="Plan type e.g. residential, business"),
    limit:     int             = Query(50, le=200),
    offset:    int             = Query(0),
    db: AsyncSession           = Depends(get_db),
):
    q = """
        SELECT p.*, i.name AS isp_name, i.slug AS isp_slug,
               ROUND(p.price_monthly / p.download_mbps, 2) AS price_per_mbps
        FROM plans p
        JOIN isps i ON i.id = p.isp_id
        WHERE p.status IN ('active','promotional')
    """
    params = {}

    if isp:       q += " AND i.slug = :isp";              params["isp"]       = isp
    if min_speed: q += " AND p.download_mbps >= :mns";    params["mns"]       = min_speed
    if max_speed: q += " AND p.download_mbps <= :mxs";    params["mxs"]       = max_speed
    if max_price: q += " AND p.price_monthly <= :mxp";    params["mxp"]       = max_price
    if bundle:    q += " AND :bundle = ANY(p.bundle_flags)"; params["bundle"]  = bundle
    if plan_type: q += " AND p.plan_type = :ptype";        params["ptype"]    = plan_type

    q += " ORDER BY p.download_mbps ASC, p.price_monthly ASC LIMIT :limit OFFSET :offset"
    params.update({"limit": limit, "offset": offset})

    result = await db.execute(text(q), params)
    rows   = result.fetchall()
    data   = [dict(r._mapping) for r in rows]
    return {"data": data, "count": len(data)}


@router.get("/compare")
async def compare_vs_worldlink(db: AsyncSession = Depends(get_db)):
    """WorldLink pricing vs every competitor at matching speed tiers."""
    result = await db.execute(text("""
        WITH wl AS (
            SELECT p.download_mbps, p.price_monthly
            FROM plans p JOIN isps i ON i.id = p.isp_id
            WHERE i.is_competitor = false AND p.status = 'active'
        )
        SELECT p.id, i.name AS competitor_name, i.slug AS competitor_slug,
               p.normalized_name, p.download_mbps,
               CAST(p.price_monthly AS FLOAT)  AS competitor_price,
               CAST(wl.price_monthly AS FLOAT) AS worldlink_price,
               ROUND(((p.price_monthly - wl.price_monthly) / wl.price_monthly) * 100, 1) AS price_diff_pct,
               p.bundle_flags, p.is_unlimited
        FROM plans p
        JOIN isps i  ON i.id = p.isp_id
        LEFT JOIN wl ON wl.download_mbps = p.download_mbps
        WHERE i.is_competitor = true AND p.status IN ('active','promotional')
        ORDER BY p.download_mbps ASC, price_diff_pct ASC
    """))
    return {"data": [dict(r._mapping) for r in result.fetchall()]}


@router.get("/{plan_id}")
async def get_plan(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT p.*, i.name AS isp_name, i.slug AS isp_slug
        FROM plans p JOIN isps i ON i.id = p.isp_id
        WHERE p.id = :plan_id
    """), {"plan_id": str(plan_id)})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"data": dict(row._mapping)}


@router.get("/{plan_id}/history")
async def get_plan_history(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT * FROM pricing_history
        WHERE plan_id = :plan_id
        ORDER BY recorded_at DESC LIMIT 100
    """), {"plan_id": str(plan_id)})
    return {"data": [dict(r._mapping) for r in result.fetchall()]}
