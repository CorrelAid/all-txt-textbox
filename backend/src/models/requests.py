from datetime import datetime

from models.base import Base
from sqlalchemy import DateTime, String, func, Text
from sqlalchemy.orm import Mapped, mapped_column


class Request(Base):
    __tablename__ = "requests"

    session: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, primary_key=True, default=func.now()
    )
    text: Mapped[str] = mapped_column(Text)
