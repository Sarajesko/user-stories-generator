from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["baja", "media", "alta", "bloqueante"]
Status = Literal["pendiente", "en progreso", "en revisión", "completada"]


class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    priority: Priority
    effort_hours: float = Field(gt=0)
    status: Status
    assigned_to: str = Field(min_length=1, max_length=100)


class TasksSchema(BaseModel):
    tasks: list[TaskSchema]
