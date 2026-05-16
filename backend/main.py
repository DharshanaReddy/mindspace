from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models
from .schemas import PostCreate, PostOut, ReplyCreate, ReplyOut, ChatMessage, ChatResponse, SuggestionRequest
from .chatbot import get_chat_response
from .suggestions import get_suggestions, list_moods

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MindSpace API",
    description="Anonymous mental health support community backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "MindSpace API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ── Posts ─────────────────────────────────────────────────────────────────────

@app.get("/posts", response_model=list[PostOut])
def list_posts(mood: str | None = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(models.Post)
    if mood:
        query = query.filter(models.Post.mood == mood)
    return query.order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()


@app.post("/posts", response_model=PostOut, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = models.Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/posts/{post_id}/upvote", response_model=PostOut)
def upvote_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.upvotes += 1
    db.commit()
    db.refresh(post)
    return post


# ── Replies ───────────────────────────────────────────────────────────────────

@app.post("/posts/{post_id}/replies", response_model=ReplyOut, status_code=201)
def add_reply(post_id: int, reply: ReplyCreate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db_reply = models.Reply(post_id=post_id, **reply.model_dump())
    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)
    return db_reply


# ── Chatbot ───────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
def chat(msg: ChatMessage):
    try:
        response = get_chat_response(msg.message, msg.mood, msg.history)
        return ChatResponse(response=response)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat error: {exc}")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
