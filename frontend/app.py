import streamlit as st
import httpx
import os
import random
import string
from datetime import datetime
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
    .logo { font-size: 2.4rem; font-weight: 800; color: #7C3AED; }
    .tagline { color: #888; font-size: 1rem; margin-bottom: 1.5rem; }
    .post-card {
        background: #fafafa; border: 1px solid #e5e7eb;
        border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;
    }
    .mood-badge {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 600; background: #ede9fe; color: #6d28d9;
    }
    .anon-name { font-weight: 600; color: #374151; }
    .timestamp { font-size: 0.78rem; color: #9ca3af; }
    .suggestion-card {
        background: #f5f3ff; border-left: 4px solid #7C3AED;
        border-radius: 8px; padding: 0.9rem; margin-bottom: 0.6rem;
    }
    .chat-user { background: #ede9fe; border-radius: 12px; padding: 0.7rem 1rem; margin: 0.3rem 0; }
    .chat-kai  { background: #f3f4f6; border-radius: 12px; padding: 0.7rem 1rem; margin: 0.3rem 0; }
</style>
""", unsafe_allow_html=True)

MOOD_EMOJIS = {
    "Happy": "😊", "Sad": "😢", "Anxious": "😰", "Angry": "😤",
    "Lonely": "🫂", "Stressed": "😩", "Hopeful": "🌟", "Exhausted": "😴",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def api(method: str, path: str, **kwargs):
    try:
        r = httpx.request(method, f"{BACKEND}{path}", timeout=15, **kwargs)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        st.error("Cannot reach the backend. Make sure the FastAPI server is running (`python -m uvicorn backend.main:app --port 8001`).")
        st.stop()
    except httpx.HTTPStatusError as e:
        st.error(f"API error {e.response.status_code}: {e.response.text}")
        return None


def random_name() -> str:
    adjectives = [
        "Quiet", "Gentle", "Brave", "Calm", "Kind", "Soft",
        "Warm", "Still", "Bold", "Wise", "Free", "Open",
    ]
    nouns = [
        "Star", "River", "Moon", "Cloud", "Wave", "Leaf",
        "Stone", "Bird", "Wind", "Rain", "Fox", "Owl",
    ]
    suffix = "".join(random.choices(string.digits, k=3))
    return f"{random.choice(adjectives)}{random.choice(nouns)}{suffix}"


def fmt_time(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y · %I:%M %p")
    except Exception:
        return ts


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_feed():
    st.markdown("## 🏠 Community Feed")
    st.caption("A safe, anonymous space to share and be heard.")

    moods_resp = api("GET", "/moods") or []
    mood_labels = ["All"] + [f"{m['emoji']} {m['mood']}" for m in moods_resp]
    selected_label = st.selectbox("Filter by mood", mood_labels)
    mood_filter = None if selected_label == "All" else selected_label.split(" ", 1)[1]

    posts = api("GET", "/posts", params={"mood": mood_filter} if mood_filter else {}) or []

    if not posts:
        st.info("No posts yet — be the first to share something.")
        return

    for post in posts:
        emoji = MOOD_EMOJIS.get(post["mood"], "")
        with st.container():
            st.markdown(f"""
<div class="post-card">
  <span class="anon-name">{post['anonymous_name']}</span>
  &nbsp;<span class="mood-badge">{emoji} {post['mood']}</span>
  &nbsp;<span class="timestamp">{fmt_time(post['created_at'])}</span>
  <p style="margin-top:0.6rem; margin-bottom:0.4rem;">{post['content']}</p>
</div>""", unsafe_allow_html=True)

            c1, c2, c3 = st.columns([1, 1, 6])
            with c1:
                if st.button(f"❤️ {post['upvotes']}", key=f"up_{post['id']}"):
                    api("POST", f"/posts/{post['id']}/upvote")
                    st.rerun()
            with c2:
                toggle_key = f"show_replies_{post['id']}"
                n_replies = len(post.get("replies", []))
                label = f"💬 {n_replies}"
                if st.button(label, key=f"btn_{post['id']}"):
                    st.session_state[toggle_key] = not st.session_state.get(toggle_key, False)

            if st.session_state.get(f"show_replies_{post['id']}", False):
                with st.expander("Replies", expanded=True):
                    for reply in post.get("replies", []):
                        st.markdown(f"**{reply['anonymous_name']}** · {fmt_time(reply['created_at'])}")
                        st.write(reply["content"])
                        st.markdown("---")

                    with st.form(key=f"reply_form_{post['id']}"):
                        name = st.text_input("Your anonymous name", value=random_name(), key=f"rname_{post['id']}")
                        content = st.text_area("Your reply", key=f"rcont_{post['id']}")
                        if st.form_submit_button("Send Reply"):
                            if content.strip():
                                api("POST", f"/posts/{post['id']}/replies",
                                    json={"anonymous_name": name, "content": content})
                                st.rerun()


def page_share():
    st.markdown("## 💬 Share Your Story")
    st.caption("Everything here is anonymous. Say what you need to say.")

    with st.form("new_post"):
        name = st.text_input(
            "Anonymous name (or keep the generated one)",
            value=st.session_state.get("anon_name", random_name()),
        )
        st.session_state["anon_name"] = name

        mood = st.selectbox(
            "How are you feeling?",
            list(MOOD_EMOJIS.keys()),
            format_func=lambda m: f"{MOOD_EMOJIS[m]} {m}",
        )

        content = st.text_area(
            "What's on your mind?",
            placeholder="You don't have to have it all figured out. Just write.",
            height=180,
        )

        submitted = st.form_submit_button("Share Anonymously", type="primary")

    if submitted:
        if len(content.strip()) < 10:
            st.warning("Please write at least 10 characters.")
        else:
            result = api("POST", "/posts", json={
                "anonymous_name": name,
                "content": content.strip(),
                "mood": mood,
            })
            if result:
                st.success("Your story has been shared. You are not alone.")
                st.balloons()


def page_mood_booster():
    st.markdown("## 🎭 Mood Booster")
    st.caption("Personalized music, movies, and wellness activities based on how you feel.")

    mood = st.selectbox(
        "How are you feeling right now?",
        list(MOOD_EMOJIS.keys()),
        format_func=lambda m: f"{MOOD_EMOJIS[m]} {m}",
    )

    if st.button("Get Suggestions", type="primary"):
        data = api("POST", "/suggestions", json={"mood": mood})
        if not data:
            return

        st.markdown(f"### {data['emoji']} Suggestions for when you feel **{mood}**")

        tab_music, tab_movies, tab_wellness = st.tabs(["🎵 Music", "🎬 Movies", "🌿 Wellness"])

        with tab_music:
            for item in data.get("music", []):
                st.markdown(f"""
<div class="suggestion-card">
  <strong>{item['title']}</strong> — {item['artist']}<br>
  <span style="color:#6d28d9; font-size:0.85rem;">{item['vibe']}</span>
</div>""", unsafe_allow_html=True)

        with tab_movies:
            cols = st.columns(min(len(data.get("movies", [])), 3))
            for i, item in enumerate(data.get("movies", [])):
                with cols[i % 3]:
                    st.markdown(f"**{item['title']}** ({item['year']})")
                    st.write(item["why"])

        with tab_wellness:
            for item in data.get("wellness", []):
                st.markdown(f"""
<div class="suggestion-card">
  <strong>{item['type']}</strong><br>{item['activity']}
</div>""", unsafe_allow_html=True)


def page_chat():
    st.markdown("## 🤖 Chat with Kai")
    st.caption("Kai is an AI companion here to listen — not to judge, just to be present with you.")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": "Hey, I'm Kai. I'm here to listen. How are you doing today?",
        })

    mood = st.selectbox(
        "Share your current mood with Kai (optional)",
        ["Rather not say"] + list(MOOD_EMOJIS.keys()),
        format_func=lambda m: f"{MOOD_EMOJIS.get(m, '')} {m}",
    )
    active_mood = None if mood == "Rather not say" else mood

    for turn in st.session_state["chat_history"]:
        if turn["role"] == "user":
            st.markdown(f'<div class="chat-user">🧑 {turn["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-kai">🤖 <strong>Kai:</strong> {turn["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Message Kai...", placeholder="Type something — anything at all.")
        send = st.form_submit_button("Send")

    if send and user_input.strip():
        st.session_state["chat_history"].append({"role": "user", "content": user_input.strip()})

        history_for_api = [
            t for t in st.session_state["chat_history"][:-1]
            if t["role"] in ("user", "assistant")
        ]
        result = api("POST", "/chat", json={
            "message": user_input.strip(),
            "mood": active_mood,
            "history": history_for_api,
        })
        if result:
            st.session_state["chat_history"].append({"role": "assistant", "content": result["response"]})
        st.rerun()

    if st.button("Clear conversation"):
        st.session_state["chat_history"] = [{
            "role": "assistant",
            "content": "Hey, I'm Kai. I'm here to listen. How are you doing today?",
        }]
        st.rerun()

    st.markdown("---")
    st.caption(
        "Kai is an AI and cannot replace professional mental health support. "
        "If you're in crisis, please reach out to the **988 Suicide & Crisis Lifeline** (call or text 988 in the US)."
    )


# ── Sidebar nav ───────────────────────────────────────────────────────────────

def main():
    with st.sidebar:
        st.markdown('<div class="logo">🧠 MindSpace</div>', unsafe_allow_html=True)
        st.markdown('<div class="tagline">You are not alone.</div>', unsafe_allow_html=True)
        st.markdown("---")

        page = st.radio(
            "Navigate",
            ["🏠 Community Feed", "💬 Share Your Story", "🎭 Mood Booster", "🤖 Chat with Kai"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.caption(
            "MindSpace is an anonymous peer support space. "
            "It does not provide medical advice. "
            "If you are in immediate danger, call emergency services."
        )

    if page == "🏠 Community Feed":
        page_feed()
    elif page == "💬 Share Your Story":
        page_share()
    elif page == "🎭 Mood Booster":
        page_mood_booster()
    elif page == "🤖 Chat with Kai":
        page_chat()


if __name__ == "__main__":
    main()
