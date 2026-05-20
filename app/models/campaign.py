import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Boolean, Numeric, Integer, ForeignKey, Date, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id:               Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    isp_id:           Mapped[int]             = mapped_column(ForeignKey("isps.id", ondelete="CASCADE"), nullable=False, index=True)
    title:            Mapped[str]             = mapped_column(Text, nullable=False)
    description:      Mapped[Optional[str]]   = mapped_column(Text)
    campaign_type:    Mapped[Optional[str]]   = mapped_column(String(50))
    discount_pct:     Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    discount_flat:    Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    bonus_speed_mbps: Mapped[Optional[int]]   = mapped_column(Integer)
    free_months:      Mapped[Optional[int]]   = mapped_column(Integer)
    applicable_types: Mapped[list]            = mapped_column(ARRAY(String), default=list)
    terms:            Mapped[Optional[str]]   = mapped_column(Text)
    source_url:       Mapped[Optional[str]]   = mapped_column(Text)
    valid_from:       Mapped[Optional[date]]  = mapped_column(Date)
    valid_to:         Mapped[Optional[date]]  = mapped_column(Date)
    is_active:        Mapped[bool]            = mapped_column(Boolean, default=True, index=True)
    raw_data:         Mapped[dict]            = mapped_column(JSONB, default=dict)
    first_seen_at:    Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at:     Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at:       Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())

    isp = relationship("Isp", back_populates="campaigns")
