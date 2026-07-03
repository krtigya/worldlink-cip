"""
Here I am writing code for the RAG (Retrieval-Augmented Generation) API endpoints.
POST /api/rag/query   — semantic plan search
POST /api/rag/ask     — full RAG with LLM answer
POST /api/rag/reindex — re-index all plans in Qdrant
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.db.session import get_db, get_sync_db
from app.rag.rag_service import RagService
from app.schemas.rag import RagQueryRequest, AskRequest, RagQueryResponse, AskResponse

router     = APIRouter(prefix="/api/rag", tags=["RAG"])
rag_service = RagService()


@router.post("/query", response_model=RagQueryResponse)
async def rag_query(body: RagQueryRequest):
    try:
        results = rag_service.search(
            query=body.q,
            min_speed=body.min_speed,
            max_speed=body.max_speed,
            max_price=body.max_price,
            bundle_flags=body.bundle_flags,
            limit=body.limit,
        )
        return {"data": results, "query": body.q}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AskResponse)
async def rag_ask(body: AskRequest):
    try:
        result = rag_service.ask(body.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reindex")
async def reindex(db: AsyncSession = Depends(get_db)):
    """Trigger full re-index of all active plans into Qdrant."""
    try:
        sync_session: Session = next(get_sync_db())
        count = rag_service.index_all_plans(sync_session)
        return {"message": f"Indexed {count} plans", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
