import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoadmapItemIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None


class RoadmapCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    objective: str | None = None
    items: list[RoadmapItemIn] = Field(min_length=1, max_length=30)


class RoadmapItemStatusIn(BaseModel):
    status: str = Field(pattern="^(pending|in_progress|completed)$")


class RoadmapItemOut(RoadmapItemIn):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_index: int
    status: str


class RoadmapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    objective: str | None
    created_at: datetime
    updated_at: datetime
    items: list[RoadmapItemOut]