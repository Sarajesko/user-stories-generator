from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from database import Base

if TYPE_CHECKING:
    from models.task import Task

PRIORITY_VALUES = ("baja", "media", "alta", "bloqueante")


class UserStory(Base):
    __tablename__ = "user_stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(200), nullable=False)
    goal: Mapped[str] = mapped_column(String(500), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    story_points: Mapped[int] = mapped_column(Integer, nullable=False)
    effort_hours: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="user_story",
        cascade="all, delete-orphan",
    )
