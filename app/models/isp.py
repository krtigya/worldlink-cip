import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Text, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


class IspStatus(str, enum.Enum):
    active            = "active"
    inactive          = "inactive"
    monitoring_paused = "monitoring_paused"


class Isp(Base):
    __tablename__ = "isps"

    id:             Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    slug:           Mapped[str]           = mapped_column(String(50), unique=True, nullable=False, index=True)
    name:           Mapped[str]           = mapped_column(String(100), nullable=False)
    website_url:    Mapped[str]           = mapped_column(Text, nullable=False)
    logo_url:       Mapped[Optional[str]] = mapped_column(Text)
    is_competitor:  Mapped[bool]          = mapped_column(Boolean, default=True, index=True)
    status:         Mapped[IspStatus]     = mapped_column(SAEnum(IspStatus), default=IspStatus.active)
    scraper_config: Mapped[dict]          = mapped_column(JSONB, default=dict)
    metadata_:      Mapped[dict]          = mapped_column("metadata", JSONB, default=dict)
    created_at:     Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:     Mapped[datetime]      = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    plans        = relationship("Plan",      back_populates="isp", cascade="all, delete-orphan")
    campaigns    = relationship("Campaign",  back_populates="isp", cascade="all, delete-orphan")
    change_logs  = relationship("ChangeLog", back_populates="isp")
    scrape_runs  = relationship("ScrapeRun", back_populates="isp")

    def __repr__(self): return f"<Isp {self.slug}>"
