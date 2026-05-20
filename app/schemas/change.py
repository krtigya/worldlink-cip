import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class ChangeLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    isp_id: int
    plan_id: Optional[uuid.UUID]
    change_type: str
    severity: str
    field_name: Optional[str]
    old_value: Optional[Any]
    new_value: Optional[Any]
    diff_pct: Optional[float]
    summary: str
    details: dict
    alert_sent: bool
    detected_at: datetime


class ChangeLogListResponse(BaseModel):
    data: list[ChangeLogResponse]
    count: int


class ChangeSummaryItem(BaseModel):
    change_type: str
    severity: str
    count: int
