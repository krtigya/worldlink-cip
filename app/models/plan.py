import enum
import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (String, Boolean, Text, DateTime, Date, Integer,
                        Numeric, ForeignKey, Enum as SAEnum, UniqueConstraint)
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


class PlanType(str, enum.Enum):
    residential = "residential"
    business    = "business"
    enterprise  = "enterprise"
    fiber       = "fiber"
    wireless    = "wireless"


class PlanStatus(str, enum.Enum):
    active       = "active"
    discontinued = "discontinued"
    promotional  = "promotional"
    coming_soon  = "coming_soon"


class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = (UniqueConstraint("isp_id", "normalized_name", name="uq_plan"),)

    id:              Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    isp_id:          Mapped[int]             = mapped_column(ForeignKey("isps.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id:     Mapped[Optional[str]]   = mapped_column(String(100))
    raw_name:        Mapped[str]             = mapped_column(Text, nullable=False)
    normalized_name: Mapped[str]             = mapped_column(String(200), nullable=False)
    plan_type:       Mapped[PlanType]        = mapped_column(SAEnum(PlanType), default=PlanType.residential, index=True)
    status:          Mapped[PlanStatus]      = mapped_column(SAEnum(PlanStatus), default=PlanStatus.active, index=True)
    download_mbps:   Mapped[int]             = mapped_column(Integer, nullable=False, index=True)
    upload_mbps:     Mapped[Optional[int]]   = mapped_column(Integer)
    speed_raw:       Mapped[Optional[str]]   = mapped_column(String(50))
    price_monthly:   Mapped[float]           = mapped_column(Numeric(10, 2), nullable=False, index=True)
    price_quarterly: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    price_annual:    Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    price_raw:       Mapped[Optional[str]]   = mapped_column(String(50))
    setup_fee:       Mapped[float]           = mapped_column(Numeric(10, 2), default=0)
    vat_included:    Mapped[bool]            = mapped_column(Boolean, default=True)
    fup_gb:          Mapped[Optional[int]]   = mapped_column(Integer)
    is_unlimited:    Mapped[bool]            = mapped_column(Boolean, default=False)
    contract_months: Mapped[int]             = mapped_column(Integer, default=1)
    bundles:         Mapped[list]            = mapped_column(JSONB, default=list)
    bundle_flags:    Mapped[list]            = mapped_column(ARRAY(String), default=list)
    description:     Mapped[Optional[str]]   = mapped_column(Text)
    scrape_url:      Mapped[Optional[str]]   = mapped_column(Text)
    raw_data:        Mapped[dict]            = mapped_column(JSONB, default=dict)
    embedding_id:    Mapped[Optional[str]]   = mapped_column(String(100))
    first_seen_at:   Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at:    Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at:      Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:      Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    isp             = relationship("Isp",            back_populates="plans")
    pricing_history = relationship("PricingHistory",  back_populates="plan", cascade="all, delete-orphan")

    @property
    def price_per_mbps(self) -> float:
        return round(float(self.price_monthly) / self.download_mbps, 2) if self.download_mbps else 0

    def __repr__(self):
        return f"<Plan {self.normalized_name} {self.download_mbps}Mbps NPR{self.price_monthly}>"
