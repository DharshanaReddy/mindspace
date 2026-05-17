# 🧠 MindSpace — Anonymous Mental Health Support Community

> A full-stack anonymous peer support platform with a **RAG-powered AI chatbot**, **GPT-4o-mini sentiment analysis**, **real-time WebSocket feed**, and **OpenAI content moderation** — built with FastAPI, LangChain, and Streamlit.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit Frontend                        │
│  Community Feed · Share Story · Mood Booster · Kai · Analytics  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST + WebSocket
┌───────────────────────────▼─────────────────────────────────────┐
│                       FastAPI Backend                            │
│                                                                  │
│  ┌─────────────────┐   ┌──────────────────────────────────┐     │
│  │  Content Flow   │   │          Kai Chatbot             │     │
│  │                 │   │                                  │     │
│  │ POST /posts     │   │  LangChain ConversationChain     │     │
│  │      │          │   │       +                          │     │
│  │      ▼          │   │  ChromaDB RAG (mental health KB) │     │
│  │  OpenAI         │   │       +                          │     │
│  │  Moderation API │   │  LangSmith Tracing               │     │
│  │      │          │   └──────────────────────────────────┘     │
│  │      ▼          │                                            │
│  │  Mood Sentiment │   ┌──────────────────────────────────┐     │
│  │  Analysis       │   │      WebSocket Manager           │     │
│  │  (GPT-4o-mini)  │   │  Real-time post/reply broadcast  │     │
│  │      │          │   └──────────────────────────────────┘     │
│  │      ▼          │                                            │
│  │  PostgreSQL      │   ┌──────────────────────────────────┐    │
│  │  (SQLAlchemy     │   │     Anonymous JWT Auth           │    │
│  │   async)        │   │  Session tokens without accounts  │    │
│  └─────────────────┘   └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Chatbot | **LangChain + GPT-4o-mini** | Conversational AI with memory |
| RAG | **ChromaDB + LangChain** | Evidence-based mental health knowledge retrieval |
| Observability | **LangSmith** | Full chain tracing per conversation |
| Sentiment | **GPT-4o-mini** | Mood classification from post text (8 categories) |
| Moderation | **OpenAI Moderation API** | Pre-publish content screening |
| Backend | **FastAPI (async)** | REST API + WebSocket support |
| Real-time | **WebSockets** | Live post/reply broadcast to all clients |
| Database | **PostgreSQL + SQLAlchemy async** | Async ORM with connection pooling |
| Auth | **Anonymous JWT** | Persistent anonymous identity (no account needed) |
| Frontend | **Streamlit + Plotly** | Multi-page UI with community analytics dashboard |
| Infrastructure | **Docker + Compose** | PostgreSQL + backend + frontend containerized |

## Features

### Community Feed
- Anonymous post sharing with 8 mood categories
- **Real-time updates** via WebSocket — new posts appear without refresh
- **AI mood detection** — GPT-4o-mini auto-classifies emotional state from post content
- **Content moderation** — every post screened through OpenAI Moderation API before publishing
- Upvoting and threaded replies

### Kai — AI Companion
- **RAG-powered** — retrieves evidence-based psychology content from ChromaDB before responding
- Grounded in CBT techniques, grounding exercises, crisis resources, and mindfulness research
- LangSmith tracing for every conversation
- Crisis protocol — surfaces 988 Lifeline when needed
- Mood-aware context — adapts tone based on user's stated emotional state

### Mood Booster
- 8 emotional categories × curated music, movies, and wellness activities
- 100+ personalized recommendations

### Analytics Dashboard
- Real-time mood distribution across the community
- AI-detected sentiment breakdown (Plotly charts)
- Active WebSocket connections counter

## Quick Start

```bash
git clone https://github.com/DharshanaReddy/mindspace
cd mindspace
cp .env.example .env  # add OPENAI_API_KEY
```

**Option A — Docker (recommended, includes PostgreSQL):**
```bash
docker-compose up --build
# Frontend: http://localhost:8501
# Backend:  http://localhost:8001/docs
```

**Option B — Local with SQLite:**
```bash
pip install -r requirements.txt

# Terminal 1 — Backend
uvicorn backend.main:app --port 8001 --reload

# Terminal 2 — Frontend
cd frontend && streamlit run app.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | OpenAI API key |
| `LANGCHAIN_API_KEY` | Recommended | LangSmith tracing key |
| `DATABASE_URL` | No | Defaults to SQLite; use PostgreSQL in production |
| `JWT_SECRET` | No | Secret for signing anonymous session JWTs |
| `BACKEND_URL` | No | Frontend → Backend URL |

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/session` | Issue anonymous JWT |
| `GET` | `/posts` | List posts (filter by mood) |
| `POST` | `/posts` | Create post (moderated + sentiment analyzed) |
| `POST` | `/posts/{id}/upvote` | Upvote a post |
| `POST` | `/posts/{id}/replies` | Reply to a post |
| `POST` | `/chat` | Message Kai (RAG chatbot) |
| `POST` | `/analyze-mood` | Classify mood from text |
| `GET` | `/analytics/overview` | Community mood/sentiment stats |
| `WS` | `/ws` | WebSocket for real-time feed |

Full interactive docs: `/docs`

## LangSmith Observability

Every Kai conversation and RAG retrieval is traced in LangSmith:
- Per-turn latency and token usage
- Retrieved document IDs (RAG transparency)
- Full chain visualization

Get a free key at [smith.langchain.com](https://smith.langchain.com)
