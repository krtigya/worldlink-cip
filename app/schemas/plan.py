"""Pydantic response schemas for Plan endpoints."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BundleItem(BaseModel):
    type: str
    name: str
    details: Optional[str] = None


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    isp_id: int
    raw_name: str
    normalized_name: str
    plan_type: str
    status: str
    download_mbps: int
    upload_mbps: Optional[int]
    price_monthly: float
    price_quarterly: Optional[float]
    price_annual: Optional[float]
    setup_fee: float
    vat_included: bool
    fup_gb: Optional[int]
    is_unlimited: bool
    contract_months: int
    bundles: list
    bundle_flags: list[str]
    description: Optional[str]
    first_seen_at: datetime
    last_seen_at: datetime


class PlanListResponse(BaseModel):
    data: list[PlanResponse]
    count: int


class PricingHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    price_monthly: float
    download_mbps: int
    bundle_flags: list[str]
    status: str
    recorded_at: datetime
