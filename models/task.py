from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.user_story import UserStory

PRIORITY_VALUES = ("baja", "media", "alta", "bloqueante")
STATUS_VALUES = ("pendiente", "en progreso", "en revisión", "completada")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    effort_hours: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    assigned_to: Mapped[str] = mapped_column(String(100), nullable=False)
    user_story_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_stories.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    user_story: Mapped["UserStory"] = relationship(
        "UserStory",
        back_populates="tasks",
    )
