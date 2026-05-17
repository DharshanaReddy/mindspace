from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .connection import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    session_token = Column(String(64), nullable=False, index=True)
    anonymous_name = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    mood = Column(String(30), nullable=False)
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(20), nullable=True)
    upvotes = Column(Integer, default=0)
    is_moderated = Column(Boolean, default=False)
    flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    replies = relationship("Reply", back_populates="post", cascade="all, delete-orphan")


class Reply(Base):
    __tablename__ = "replies"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    session_token = Column(String(64), nullable=False)
    anonymous_name = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    post = relationship("Post", back_populates="replies")
