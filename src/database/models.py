from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from src.database.database import Base
from datetime import datetime

class Documents(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    rubrics: Mapped[list[str]] = mapped_column(ARRAY(String))
    text: Mapped[str]
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=False))
