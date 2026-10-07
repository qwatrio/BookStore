from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentUser(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    text: str


class CommentResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
    user: CommentUser

    model_config = ConfigDict(from_attributes=True)
