import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, Numeric, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


class ChangeType(str, enum.Enum):
    price_decrease   = "price_decrease"
    price_increase   = "price_increase"
    plan_added       = "plan_added"
    plan_removed     = "plan_removed"
    speed_change     = "speed_change"
    bundle_added     = "bundle_added"
    bundle_removed   = "bundle_removed"
    campaign_started = "campaign_started"
    campaign_ended   = "campaign_ended"
    fup_change       = "fup_change"
    contract_change  = "contract_change"


class SeverityLevel(str, enum.Enum):
    low      = "low"
    medium   = "medium"
    high     = "high"
    critical = "critical"


class ChangeLog(Base):
    __tablename__ = "change_logs"

    id:             Mapped[uuid.UUID]           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    isp_id:         Mapped[int]                 = mapped_column(ForeignKey("isps.id"), nullable=False, index=True)
    plan_id:        Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("plans.id"), index=True)
    campaign_id:    Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"))
    change_type:    Mapped[ChangeType]          = mapped_column(SAEnum(ChangeType), nullable=False, index=True)
    severity:       Mapped[SeverityLevel]       = mapped_column(SAEnum(SeverityLevel), default=SeverityLevel.medium, index=True)
    field_name:     Mapped[Optional[str]]       = mapped_column(String(100))
    old_value:      Mapped[Optional[dict]]      = mapped_column(JSONB)
    new_value:      Mapped[Optional[dict]]      = mapped_column(JSONB)
    diff_pct:       Mapped[Optional[float]]     = mapped_column(Numeric(8, 2))
    summary:        Mapped[str]                 = mapped_column(Text, nullable=False)
    details:        Mapped[dict]                = mapped_column(JSONB, default=dict)
    alert_sent:     Mapped[bool]                = mapped_column(Boolean, default=False, index=True)
    alert_sent_at:  Mapped[Optional[datetime]]  = mapped_column(DateTime(timezone=True))
    alert_channels: Mapped[list]                = mapped_column(ARRAY(String), default=list)
    suppressed:     Mapped[bool]                = mapped_column(Boolean, default=False)
    scrape_run_id:  Mapped[Optional[str]]       = mapped_column(String(36))
    detected_at:    Mapped[datetime]            = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    isp = relationship("Isp", back_populates="change_logs")
