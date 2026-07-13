from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["baja", "media", "alta", "bloqueante"]


class UserStorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=200)
    goal: str = Field(min_length=1, max_length=500)
    reason: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1)
    priority: Priority
    story_points: int = Field(ge=1, le=8)
    effort_hours: float = Field(gt=0)


class UserStoriesSchema(BaseModel):
    user_stories: list[UserStorySchema]
