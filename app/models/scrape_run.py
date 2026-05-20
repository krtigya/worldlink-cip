import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id:               Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    isp_id:           Mapped[int]                = mapped_column(ForeignKey("isps.id"), nullable=False, index=True)
    status:           Mapped[str]                = mapped_column(String(20), default="pending", index=True)
    plans_found:      Mapped[int]                = mapped_column(Integer, default=0)
    plans_new:        Mapped[int]                = mapped_column(Integer, default=0)
    plans_updated:    Mapped[int]                = mapped_column(Integer, default=0)
    plans_removed:    Mapped[int]                = mapped_column(Integer, default=0)
    campaigns_found:  Mapped[int]                = mapped_column(Integer, default=0)
    changes_detected: Mapped[int]                = mapped_column(Integer, default=0)
    error_message:    Mapped[Optional[str]]      = mapped_column(Text)
    error_stack:      Mapped[Optional[str]]      = mapped_column(Text)
    duration_ms:      Mapped[Optional[int]]      = mapped_column(Integer)
    scraper_version:  Mapped[Optional[str]]      = mapped_column(String(20))
    started_at:       Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at:     Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    isp = relationship("Isp", back_populates="scrape_runs")
