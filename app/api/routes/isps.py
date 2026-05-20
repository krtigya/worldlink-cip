"""
GET /api/isps — list all ISPs
GET /api/isps/{slug} — single ISP detail
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter(prefix="/api/isps", tags=["ISPs"])


@router.get("")
async def list_isps(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text(
        "SELECT id, slug, name, website_url, is_competitor, status FROM isps ORDER BY is_competitor, name"
    ))
    return {"data": [dict(r._mapping) for r in result.fetchall()]}


@router.get("/{slug}")
async def get_isp(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM isps WHERE slug = :slug"), {"slug": slug}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="ISP not found")
    return {"data": dict(row._mapping)}
