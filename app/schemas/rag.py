from typing import Optional, Any
from pydantic import BaseModel


class RagQueryRequest(BaseModel):
    q: str
    min_speed: Optional[int] = None
    max_speed: Optional[int] = None
    max_price: Optional[float] = None
    bundle_flags: Optional[list[str]] = None
    limit: int = 5


class AskRequest(BaseModel):
    question: str


class RagResult(BaseModel):
    plan_id: str
    isp_name: str
    normalized_name: str
    download_mbps: int
    price_monthly: float
    bundle_flags: list[str]
    is_unlimited: bool
    score: float
    explanation: Optional[str] = None


class RagQueryResponse(BaseModel):
    data: list[RagResult]
    query: str


class AskResponse(BaseModel):
    answer: str
    sources: list[RagResult]
