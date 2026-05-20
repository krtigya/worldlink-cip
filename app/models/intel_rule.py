from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, Integer, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from .base import Base
from .change_log import SeverityLevel


class IntelRule(Base):
    __tablename__ = "intel_rules"

    id:             Mapped[int]                  = mapped_column(primary_key=True, autoincrement=True)
    rule_key:       Mapped[str]                  = mapped_column(String(100), unique=True, nullable=False)
    name:           Mapped[str]                  = mapped_column(Text, nullable=False)
    description:    Mapped[Optional[str]]        = mapped_column(Text)
    condition:      Mapped[dict]                 = mapped_column(JSONB, nullable=False)
    severity:       Mapped[SeverityLevel]        = mapped_column(SAEnum(SeverityLevel), default=SeverityLevel.medium)
    is_enabled:     Mapped[bool]                 = mapped_column(Boolean, default=True)
    channels:       Mapped[list]                 = mapped_column(ARRAY(String), default=list)
    cooldown_hours: Mapped[int]                  = mapped_column(Integer, default=24)
    last_triggered: Mapped[Optional[datetime]]   = mapped_column(DateTime(timezone=True))
    trigger_count:  Mapped[int]                  = mapped_column(Integer, default=0)
    created_at:     Mapped[datetime]             = mapped_column(DateTime(timezone=True), server_default=func.now())
