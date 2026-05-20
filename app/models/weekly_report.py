import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import Text, Date, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from .base import Base


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id:           Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_week:  Mapped[date]               = mapped_column(Date, unique=True, nullable=False)
    summary:      Mapped[Optional[str]]      = mapped_column(Text)
    full_report:  Mapped[dict]               = mapped_column(JSONB, default=dict)
    html_content: Mapped[Optional[str]]      = mapped_column(Text)
    generated_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now())
    sent_at:      Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    recipients:   Mapped[list]               = mapped_column(ARRAY(Text), default=list)
