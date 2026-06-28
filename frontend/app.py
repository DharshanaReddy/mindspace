"""
MindSpace — Streamlit Frontend
Anonymous mental health support community with real-time feed,
AI chatbot (Kai), mood analysis, and community analytics.
"""

import streamlit as st
import httpx
import os
import random
import string
from dotenv import load_dotenv

load_dotenv()

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8001")

st.set_page_config(
    page_title="MindSpace",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .brand { font-size:2rem; font-weight:800; color:#7C3AED; letter-spacing:-0.5px; }
    .tagline { color:#9ca3af; font-size:0.9rem; }
    .post-card {
        background:#fff; border:1px solid #e5e7eb; border-radius:14px;
        padding:1.2rem; margin-bottom:1rem;
        box-shadow:0 1px 3px rgba(0,0,0,0.06);
        transition: box-shadow 0.2s;
    }
    .mood-chip { display:inline-block; background:#ede9fe; color:#6d28d9;
                 border-radius:20px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
    .sentiment-chip { display:inline-block; background:#f0fdf4; color:#16a34a;
                      border-radius:20px; padding:2px 10px; font-size:0.72rem; margin-left:4px; }
    .anon-name { font-weight:700; color:#1f2937; font-size:0.95rem; }
    .timestamp { color:#9ca3af; font-size:0.75rem; }
    .tech-badge { display:inline-block; background:#f1f5f9; color:#475569;
                  border-radius:6px; padding:2px 8px; font-size:0.72rem;
                  font-family:monospace; margin:2px; }
    .chat-user { background:#ede9fe; border-radius:14px 14px 4px 14px;
                 padding:0.8rem 1rem; margin:0.3rem 0; max-width:85%; margin-left:auto; }
    .chat-kai { background:#f9fafb; border:1px solid #e5e7eb;
                border-radius:14px 14px 14px 4px;
                padding:0.8rem 1rem; margin:0.3rem 0; max-width:85%; }
    .section-header { font-size:1.4rem; font-weight:700; color:#1f2937; margin-bottom:0.3rem; }
</style>
""", unsafe_allow_html=True)

MOOD_EMOJIS = {
    "Happy": "😊", "Sad": "😢", "Anxious": "😰", "Angry": "😤",
    "Lonely": "🫂", "Stressed": "😩", "Hopeful": "🌟", "Exhausted": "😴",
}


# ── API helpers ───────────────────────────────────────────────────────────────

def api(method: str, path: str, **kwargs):
    try:
        headers = kwargs.pop("headers", {})
        if "jwt" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state['jwt']}"
        r = httpx.request(method, f"{BACKEND}{path}", timeout=30, headers=headers, **kwargs)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        st.error("Cannot reach the backend. Make sure the FastAPI server is running on port 8001.")
        st.stop()
    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", e.response.text) if e.response.content else str(e)
        st.error(f"Error: {detail}")
        return None


def ensure_session():
    if "session_token" not in st.session_state:
        result = api("POST", "/auth/session")
        if result:
            st.session_state["session_token"] = result["session_token"]
            st.session_state["jwt"] = result["jwt"]


def random_name() -> str:
    adj = ["Quiet", "Gentle", "Brave", "Calm", "Kind", "Soft", "Warm", "Still", "Bold", "Wise"]
    noun = ["Star", "River", "Moon", "Cloud", "Wave", "Leaf", "Stone", "Bird", "Wind", "Fox"]
    return f"{random.choice(adj)}{random.choice(noun)}{''.join(random.choices(string.digits, k=3))}"


def fmt_time(ts: str) -> str:
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%b %d · %I:%M %p")
    except Exception:
        return ts


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_feed():
    st.markdown('<div class="section-header">🏠 Community Feed</div>', unsafe_allow_html=True)
    st.caption("Anonymous stories shared in real time. You are not alone.")

    moods_data = api("GET", "/moods") or []
    filter_col, refresh_col = st.columns([4, 1])
    with filter_col:
        mood_options = ["All Moods"] + [f"{m['emoji']} {m['mood']}" for m in moods_data]
        selected = st.selectbox("Filter by mood", mood_options, label_visibility="collapsed")
    with refresh_col:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    mood_filter = None if selected == "All Moods" else selected.split(" ", 1)[1]
    posts = api("GET", "/posts", params={"mood": mood_filter} if mood_filter else {}) or []

    if not posts:
        st.info("No posts yet — be the first to share something.")
        return

    for post in posts:
        emoji = MOOD_EMOJIS.get(post["mood"], "")
        sentiment = post.get("sentiment_label", "")
        sentiment_html = f'<span class="sentiment-chip">🧠 {sentiment}</span>' if sentiment else ""

        st.markdown(f"""
<div class="post-card">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.6rem">
    <span class="anon-name">{post['anonymous_name']}</span>
    <span class="mood-chip">{emoji} {post['mood']}</span>
    {sentiment_html}
    <span class="timestamp" style="margin-left:auto">{fmt_time(post['created_at'])}</span>
  </div>
  <div style="color:#374151;line-height:1.6">{post['content']}</div>
</div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 1, 6])
        with c1:
            if st.button(f"❤️ {post['upvotes']}", key=f"up_{post['id']}"):
                api("POST", f"/posts/{post['id']}/upvote")
                st.rerun()
        with c2:
            n_replies = len(post.get("replies", []))
            if st.button(f"💬 {n_replies}", key=f"rep_{post['id']}"):
                key = f"show_{post['id']}"
                st.session_state[key] = not st.session_state.get(key, False)

        if st.session_state.get(f"show_{post['id']}", False):
            with st.container():
                for reply in post.get("replies", []):
                    st.markdown(
                        f"↳ **{reply['anonymous_name']}** · {fmt_time(reply['created_at'])}  \n{reply['content']}"
                    )
                with st.form(f"rf_{post['id']}", clear_on_submit=True):
                    rname = st.text_input("Name", value=random_name(), key=f"rn_{post['id']}")
                    rcontent = st.text_area("Your reply", key=f"rc_{post['id']}", height=80)
                    if st.form_submit_button("Send"):
                        if rcontent.strip():
                            api("POST", f"/posts/{post['id']}/replies",
                                json={"anonymous_name": rname, "content": rcontent.strip()})
                            st.rerun()


def page_share():
    st.markdown('<div class="section-header">💬 Share Your Story</div>', unsafe_allow_html=True)
    st.caption("Everything here is anonymous and moderated for community safety.")

    if "detected_mood" not in st.session_state:
        st.session_state["detected_mood"] = "Stressed"

    with st.form("share_form"):
        name = st.text_input("Anonymous name", value=st.session_state.get("anon_name", random_name()))
        st.session_state["anon_name"] = name

        content = st.text_area(
            "What's on your mind?",
            placeholder="You don't have to have it figured out. Just write.",
            height=160,
        )

        if content.strip():
            st.caption("💡 AI will auto-detect your mood — or override below.")

        mood = st.selectbox(
            "Your mood",
            list(MOOD_EMOJIS.keys()),
            index=list(MOOD_EMOJIS.keys()).index(st.session_state.get("detected_mood", "Stressed")),
            format_func=lambda m: f"{MOOD_EMOJIS[m]} {m}",
        )

        submitted = st.form_submit_button("Share Anonymously 🔒", type="primary")

    if submitted:
        if len(content.strip()) < 10:
            st.warning("Write at least 10 characters.")
        else:
            with st.spinner("Analyzing mood & running moderation..."):
                mood_result = api("POST", "/analyze-mood", json={"text": content.strip()})
                if mood_result:
                    st.session_state["detected_mood"] = mood_result.get("detected_mood", mood)
                    detected = mood_result.get("detected_mood", mood)
                    conf = mood_result.get("confidence", 0)
                    st.info(f"🧠 Detected mood: **{detected}** (confidence: {conf:.0%}) — {mood_result.get('explanation','')}")

            result = api("POST", "/posts", json={
                "anonymous_name": name,
                "content": content.strip(),
                "mood": mood,
            })
            if result:
                st.success("Shared. You are not alone. 💜")
                st.balloons()


def page_mood_booster():
    st.markdown('<div class="section-header">🎭 Mood Booster</div>', unsafe_allow_html=True)
    st.caption("Personalized music, movies, and wellness activities based on how you feel.")

    mood = st.selectbox(
        "Current mood",
        list(MOOD_EMOJIS.keys()),
        format_func=lambda m: f"{MOOD_EMOJIS[m]} {m}",
    )

    if st.button("Get Suggestions", type="primary"):
        data = api("POST", "/suggestions", json={"mood": mood})
        if not data:
            return

        st.markdown(f"### {data['emoji']} When you feel **{mood}**")
        t1, t2, t3 = st.tabs(["🎵 Music", "🎬 Movies", "🌿 Wellness"])

        with t1:
            for item in data.get("music", []):
                st.markdown(f"""
<div style="background:#f5f3ff;border-left:3px solid #7C3AED;
     border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin-bottom:0.5rem">
  <strong>{item['title']}</strong> — {item['artist']}<br>
  <span style="color:#7C3AED;font-size:0.82rem">{item['vibe']}</span>
</div>""", unsafe_allow_html=True)

        with t2:
            cols = st.columns(min(len(data.get("movies", [])), 3))
            for i, item in enumerate(data.get("movies", [])):
                with cols[i % 3]:
                    st.markdown(f"**{item['title']}** ({item['year']})")
                    st.write(item["why"])

        with t3:
            for item in data.get("wellness", []):
                st.markdown(f"""
<div style="background:#f0fdf4;border-left:3px solid #22c55e;
     border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin-bottom:0.5rem">
  <span style="font-size:0.75rem;font-weight:600;color:#16a34a;text-transform:uppercase">
    {item['type']}</span><br>{item['activity']}
</div>""", unsafe_allow_html=True)


def page_chat():
    st.markdown('<div class="section-header">🤖 Chat with Kai</div>', unsafe_allow_html=True)
    st.caption("Kai is a RAG-powered AI companion. Grounded in evidence-based mental health resources.")

    st.markdown(
        '<span class="tech-badge">LangChain</span>'
        '<span class="tech-badge">ChromaDB RAG</span>'
        '<span class="tech-badge">LangSmith</span>'
        '<span class="tech-badge">Groq LLaMA 3.1</span>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [{
            "role": "assistant",
            "content": "Hey, I'm Kai. I'm here to listen — not to judge, just to be present. How are you doing today?",
        }]

    mood = st.selectbox(
        "Share your mood with Kai",
        ["Prefer not to say"] + list(MOOD_EMOJIS.keys()),
        format_func=lambda m: f"{MOOD_EMOJIS.get(m, '')} {m}",
    )
    active_mood = None if mood == "Prefer not to say" else mood

    for turn in st.session_state["chat_history"]:
        if turn["role"] == "user":
            st.markdown(f'<div class="chat-user">🧑 {turn["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-kai">🤖 <strong>Kai:</strong> {turn["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Message Kai...", placeholder="Say anything — Kai is here.")
        send = st.form_submit_button("Send →")

    if send and user_input.strip():
        st.session_state["chat_history"].append({"role": "user", "content": user_input.strip()})
        with st.spinner("Kai is thinking..."):
            result = api("POST", "/chat", json={
                "message": user_input.strip(),
                "mood": active_mood,
                "history": st.session_state["chat_history"][:-1],
            })
        if result:
            st.session_state["chat_history"].append({"role": "assistant", "content": result["response"]})
        st.rerun()

    if st.button("Clear conversation"):
        st.session_state["chat_history"] = [{
            "role": "assistant",
            "content": "Hey, I'm Kai. I'm here to listen — not to judge, just to be present. How are you doing today?",
        }]
        st.rerun()

    st.markdown("---")
    st.caption("Kai is an AI and cannot replace professional support. In crisis? Call/text **988** (US).")


def page_analytics():
    import plotly.graph_objects as go
    import plotly.express as px

    st.markdown('<div class="section-header">📊 Community Analytics</div>', unsafe_allow_html=True)
    st.caption("Real-time sentiment and mood trends across the MindSpace community.")

    data = api("GET", "/analytics/overview")
    if not data:
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Posts", data.get("total_posts", 0))
    c2.metric("Total Replies", data.get("total_replies", 0))
    c3.metric("Active Connections", data.get("active_connections", 0))

    st.markdown("---")
    col_mood, col_sentiment = st.columns(2)

    mood_dist = data.get("mood_distribution", [])
    if mood_dist:
        with col_mood:
            st.markdown("**Mood Distribution**")
            fig = px.bar(
                x=[d["mood"] for d in mood_dist],
                y=[d["count"] for d in mood_dist],
                color=[d["mood"] for d in mood_dist],
                labels={"x": "Mood", "y": "Posts"},
            )
            fig.update_layout(showlegend=False, height=300, margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    sentiment_dist = data.get("sentiment_distribution", [])
    if sentiment_dist:
        with col_sentiment:
            st.markdown("**AI-Detected Sentiment Distribution**")
            fig = go.Figure(go.Pie(
                labels=[d["sentiment"] for d in sentiment_dist],
                values=[d["count"] for d in sentiment_dist],
                hole=0.4,
            ))
            fig.update_layout(height=300, margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ensure_session()

    with st.sidebar:
        st.markdown('<div class="brand">🧠 MindSpace</div>', unsafe_allow_html=True)
        st.markdown('<div class="tagline">You are not alone.</div>', unsafe_allow_html=True)
        st.markdown("---")

        page = st.radio(
            "Navigate",
            ["🏠 Community Feed", "💬 Share Your Story", "🎭 Mood Booster", "🤖 Chat with Kai", "📊 Analytics"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("**Tech Stack**")
        for badge in ["LangChain", "ChromaDB RAG", "LangSmith", "FastAPI", "WebSockets",
                       "Groq LLaMA 3.1", "Keyword Moderation", "SQLAlchemy", "JWT Auth"]:
            st.markdown(f'<span class="tech-badge">{badge}</span>', unsafe_allow_html=True)

        st.markdown("")
        st.caption("Not a replacement for professional mental health support.")

    pages = {
        "🏠 Community Feed": page_feed,
        "💬 Share Your Story": page_share,
        "🎭 Mood Booster": page_mood_booster,
        "🤖 Chat with Kai": page_chat,
        "📊 Analytics": page_analytics,
    }
    pages[page]()


if __name__ == "__main__":
    main()
