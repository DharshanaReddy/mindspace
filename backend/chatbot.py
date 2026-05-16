from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are Kai, a compassionate and empathetic AI companion on MindSpace — an anonymous mental health support community.

Your role:
- Provide warm, non-judgmental emotional support
- Actively listen and validate feelings
- Gently ask clarifying questions to understand what someone is going through
- Offer grounding techniques, breathing exercises, or coping strategies when appropriate
- Remind users they are not alone and that their feelings are valid
- Encourage professional help when the situation seems serious (without being alarmist)

Tone guidelines:
- Warm, human, and conversational — never clinical or robotic
- Short, focused responses (2-4 sentences usually) unless more depth is clearly needed
- Never minimize feelings with toxic positivity ("just cheer up!")
- Never give medical diagnoses or replace a therapist
- If someone expresses thoughts of self-harm, respond with care and direct them to a crisis line (e.g., 988 Suicide & Crisis Lifeline in the US)

You are not here to solve problems — you are here to hold space, listen, and gently guide."""


def get_chat_response(message: str, mood: str | None, history: list[dict]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured")

    client = OpenAI(api_key=api_key)

    system = SYSTEM_PROMPT
    if mood:
        system += f"\n\nThe user has indicated they are currently feeling: {mood}. Be especially attuned to this emotional state."

    messages = [{"role": "system", "content": system}]

    # Include conversation history (cap at last 10 turns to stay within token limits)
    for turn in history[-10:]:
        if turn.get("role") in ("user", "assistant") and turn.get("content"):
            messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.8,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()
