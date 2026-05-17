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
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    upvotes: int
    created_at: datetime
    replies: list[ReplyOut] = []
    model_config = {"from_attributes": True}


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    mood: Optional[str] = None
    history: list[dict] = []


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []


class SuggestionRequest(BaseModel):
    mood: str


class MoodAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=2000)


class MoodAnalysisResponse(BaseModel):
    detected_mood: str
    confidence: float
    sentiment: str
    explanation: str
