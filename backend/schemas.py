from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReplyCreate(BaseModel):
    anonymous_name: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=1000)


class ReplyOut(BaseModel):
    id: int
    post_id: int
    anonymous_name: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PostCreate(BaseModel):
    anonymous_name: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=10, max_length=2000)
    mood: str = Field(..., min_length=1, max_length=30)


class PostOut(BaseModel):
    id: int
    anonymous_name: str
    content: str
    mood: str
    created_at: datetime
    upvotes: int
    replies: list[ReplyOut] = []

    model_config = {"from_attributes": True}


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    mood: Optional[str] = None
    history: list[dict] = []


class ChatResponse(BaseModel):
    response: str


class SuggestionRequest(BaseModel):
    mood: str
