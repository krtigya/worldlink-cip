import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, Integer, Numeric, ForeignKey, String, DateTime, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


class PricingHistory(Base):
    __tablename__ = "pricing_history"

    id:              Mapped[int]             = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    plan_id:         Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    isp_id:          Mapped[int]             = mapped_column(ForeignKey("isps.id"), nullable=False, index=True)
    price_monthly:   Mapped[float]           = mapped_column(Numeric(10, 2), nullable=False)
    price_quarterly: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    price_annual:    Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    download_mbps:   Mapped[int]             = mapped_column(Integer, nullable=False)
    upload_mbps:     Mapped[Optional[int]]   = mapped_column(Integer)
    fup_gb:          Mapped[Optional[int]]   = mapped_column(Integer)
    bundle_flags:    Mapped[list]            = mapped_column(ARRAY(String), default=list)
    status:          Mapped[str]             = mapped_column(String(20), nullable=False)
    change_reason:   Mapped[Optional[str]]   = mapped_column(Text)
    scrape_run_id:   Mapped[Optional[str]]   = mapped_column(String(36))
    recorded_at:     Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    plan = relationship("Plan", back_populates="pricing_history")
