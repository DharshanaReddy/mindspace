"""
MindSpace API — FastAPI Backend
Anonymous mental health support platform with RAG chatbot, sentiment analysis,
real-time WebSockets, and OpenAI content moderation.
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional

from .config import get_settings
from .database.connection import init_db, get_db
from .database import models
from .database.schemas import (
    PostCreate, PostOut, ReplyCreate, ReplyOut,
    ChatMessage, ChatResponse, SuggestionRequest,
    MoodAnalysisRequest, MoodAnalysisResponse,
)
from .ml.sentiment import analyze_mood
from .rag.chatbot import get_kai_response
from .rag.vectorstore import retrieve_mental_health_context
from .websocket.manager import manager
from .moderation.moderator import moderate_content
from .auth.tokens import generate_session_token, create_jwt, decode_jwt
from .suggestions import get_suggestions, list_moods

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        retrieve_mental_health_context("warmup", n_results=1)
        logger.info("ChromaDB ready")
    except Exception as e:
        logger.warning(f"ChromaDB warmup: {e}")
    yield


app = FastAPI(
    title="MindSpace API",
    description=(
        "Anonymous mental health support community — "
        "RAG chatbot (Groq LLaMA 3.1), LangSmith-traced sentiment analysis, "
        "real-time WebSocket feed, and keyword-based content moderation."
    ),
    version="2.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/auth/session")
def create_session():
    """Issue an anonymous JWT session token."""
    token = generate_session_token()
    jwt_token = create_jwt(token)
    return {"session_token": token, "jwt": jwt_token, "expires_in_hours": settings.jwt_expire_hours}


def get_session(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        return generate_session_token()
    token = authorization.split(" ", 1)[1]
    session = decode_jwt(token)
    return session or generate_session_token()


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "MindSpace API",
        "version": "2.0.0",
        "features": ["RAG chatbot", "Sentiment analysis", "WebSockets", "Content moderation", "Anonymous JWT"],
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "active_connections": manager.connection_count}


# ── Mood Analysis ─────────────────────────────────────────────────────────────

@app.post("/analyze-mood", response_model=MoodAnalysisResponse)
async def analyze_mood_endpoint(req: MoodAnalysisRequest):
    result = await analyze_mood(req.text)
    return MoodAnalysisResponse(
        detected_mood=result.get("detected_mood", "Stressed"),
        confidence=result.get("confidence", 0.5),
        sentiment=result.get("sentiment", "neutral"),
        explanation=result.get("explanation", ""),
    )


# ── Posts ─────────────────────────────────────────────────────────────────────

@app.get("/posts", response_model=list[PostOut])
async def list_posts(
    mood: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(models.Post).where(models.Post.flagged == False)
    if mood:
        query = query.where(models.Post.mood == mood)
    query = query.order_by(desc(models.Post.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


MAX_POST_LENGTH = 2000
MAX_CHAT_LENGTH = 1000


@app.post("/posts", response_model=PostOut, status_code=201)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    session: str = Depends(get_session),
):
    if len(post.content.strip()) == 0:
        raise HTTPException(status_code=422, detail="Post content cannot be empty.")
    if len(post.content) > MAX_POST_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Post exceeds maximum length of {MAX_POST_LENGTH} characters.",
        )

    # Content moderation
    mod = await moderate_content(post.content)
    if mod.flagged:
        raise HTTPException(
            status_code=422,
            detail=f"Content flagged by moderation ({mod.reason}). Please review community guidelines.",
        )

    # Sentiment analysis
    sentiment_data = await analyze_mood(post.content)

    db_post = models.Post(
        session_token=session,
        anonymous_name=post.anonymous_name,
        content=post.content,
        mood=post.mood,
        sentiment_label=sentiment_data.get("detected_mood"),
        sentiment_score=sentiment_data.get("confidence"),
        is_moderated=True,
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)

    # Broadcast to all WebSocket clients
    await manager.broadcast("new_post", {
        "id": db_post.id,
        "anonymous_name": db_post.anonymous_name,
        "mood": db_post.mood,
        "sentiment_label": db_post.sentiment_label,
        "preview": post.content[:100] + "..." if len(post.content) > 100 else post.content,
    })

    return db_post


@app.post("/posts/{post_id}/upvote", response_model=PostOut)
async def upvote_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.upvotes += 1
    await db.commit()
    await db.refresh(post)
    return post


@app.post("/posts/{post_id}/replies", response_model=ReplyOut, status_code=201)
async def add_reply(
    post_id: int,
    reply: ReplyCreate,
    db: AsyncSession = Depends(get_db),
    session: str = Depends(get_session),
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    mod = await moderate_content(reply.content)
    if mod.flagged:
        raise HTTPException(status_code=422, detail="Reply flagged by moderation.")

    db_reply = models.Reply(
        post_id=post_id,
        session_token=session,
        anonymous_name=reply.anonymous_name,
        content=reply.content,
    )
    db.add(db_reply)
    await db.commit()
    await db.refresh(db_reply)

    await manager.broadcast("new_reply", {"post_id": post_id, "reply_id": db_reply.id})
    return db_reply


# ── Chatbot ───────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(msg: ChatMessage):
    if not msg.message or not msg.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")
    if len(msg.message) > MAX_CHAT_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Message exceeds maximum length of {MAX_CHAT_LENGTH} characters.",
        )
    try:
        response, sources = get_kai_response(msg.message, msg.mood, msg.history)
        return ChatResponse(response=response, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {e}")


# ── Suggestions ───────────────────────────────────────────────────────────────

@app.get("/moods")
def moods():
    return list_moods()


@app.post("/suggestions")
def suggestions(req: SuggestionRequest):
    result = get_suggestions(req.mood)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ── Analytics ─────────────────────────────────────────────────────────────────

@app.get("/analytics/overview")
async def analytics_overview(db: AsyncSession = Depends(get_db)):
    total_posts = await db.scalar(select(func.count(models.Post.id)))
    total_replies = await db.scalar(select(func.count(models.Reply.id)))

    mood_result = await db.execute(
        select(models.Post.mood, func.count(models.Post.id).label("count"))
        .group_by(models.Post.mood)
        .order_by(desc("count"))
    )
    mood_dist = [{"mood": r.mood, "count": r.count} for r in mood_result]

    sentiment_result = await db.execute(
        select(models.Post.sentiment_label, func.count(models.Post.id).label("count"))
        .where(models.Post.sentiment_label != None)
        .group_by(models.Post.sentiment_label)
        .order_by(desc("count"))
    )
    sentiment_dist = [{"sentiment": r.sentiment_label, "count": r.count} for r in sentiment_result]

    return {
        "total_posts": total_posts,
        "total_replies": total_replies,
        "active_connections": manager.connection_count,
        "mood_distribution": mood_dist,
        "sentiment_distribution": sentiment_dist,
    }


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await manager.send_to(websocket, "connected", {
            "message": "Connected to MindSpace real-time feed",
            "active_users": manager.connection_count,
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
