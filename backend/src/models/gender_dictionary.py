from datetime import datetime

from models.base import Base
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class GenderDictionary(Base):
    __tablename__ = "gender_dictionary"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    femininum: Mapped[str] = mapped_column(String)
    masculinum: Mapped[str] = mapped_column(String)
    comment: Mapped[str] = mapped_column(String)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    suggestions: Mapped[list["GenderDictionarySuggestion"]] = relationship()


class GenderDictionarySuggestion(Base):
    __tablename__ = "gender_dictionary_suggestions"

    gender_dictionary_id: Mapped[int] = mapped_column(
        ForeignKey("gender_dictionary.id"),
        primary_key=True,
    )
    type: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )
    value: Mapped[str] = mapped_column(String)
