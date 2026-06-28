"""
Kai — RAG-powered mental health support chatbot.
Uses LangChain + ChromaDB for grounded, evidence-based responses.
Every conversation traced with LangSmith.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langsmith import traceable
import logging
from .vectorstore import retrieve_mental_health_context
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

KAI_SYSTEM_PROMPT = """You are Kai, a compassionate AI mental health companion on MindSpace.

Your character:
- Warm, empathetic, and non-judgmental — you hold space without rushing to fix
- Trauma-informed: you don't push people to share more than they're ready for
- Evidence-informed: you draw on CBT, DBT, and mindfulness when helpful, but never diagnose
- Honest: you acknowledge when something is beyond your scope and encourage professional help
- Concise: 2-4 sentences usually — presence over length

What you do:
- Actively listen and reflect feelings back before offering any suggestions
- Ask one thoughtful open question at a time — never interrogate
- Offer grounding techniques, breathing exercises, or reframing when appropriate
- Affirm that seeking support is an act of courage, not weakness
- Remind users they are not alone — millions face similar struggles

What you never do:
- Diagnose, label, or prescribe anything
- Give toxic positivity ("just think positive!", "everything happens for a reason")
- Minimize suffering ("at least...", "it could be worse")
- Replace a licensed therapist or crisis counselor

Crisis protocol: If someone expresses thoughts of self-harm, suicide, or being in danger,
respond with genuine care first, then provide crisis resources:
- US: Call or text 988 (Suicide & Crisis Lifeline) — 24/7, free, confidential
- US Text: Text HOME to 741741 (Crisis Text Line)
- International: findahelpline.com lists crisis lines for 80+ countries
- Emergency: Call local emergency services (911 US, 999 UK, 112 EU) if in immediate danger

Grounding in knowledge: You have access to evidence-based mental health resources.
When relevant, weave in specific techniques from this context — don't quote directly, make it conversational."""

MOOD_CONTEXT = {
    "Sad": "The user is feeling sad or depressed. Lead with validation before any suggestions.",
    "Anxious": "The user is feeling anxious or worried. Consider grounding techniques.",
    "Angry": "The user is feeling angry or frustrated. Validate the feeling first, don't rush to de-escalate.",
    "Lonely": "The user is feeling lonely or isolated. Emphasize connection and that their feelings are valid.",
    "Stressed": "The user is feeling stressed or overwhelmed. Practical coping strategies may help.",
    "Hopeful": "The user is feeling hopeful or motivated. Nurture and affirm this energy.",
    "Exhausted": "The user is feeling exhausted or burnt out. Permission to rest is often what they need.",
    "Happy": "The user is feeling happy. Affirm and celebrate with them.",
}


@traceable(name="kai-chatbot", run_type="chain")
def get_kai_response(message: str, mood: str | None, history: list[dict]) -> tuple[str, list[str]]:
    """
    Generate a grounded, empathetic response from Kai.
    Returns (response_text, rag_source_ids).
    """
    # RAG: retrieve relevant knowledge for this message
    rag_context, source_ids = retrieve_mental_health_context(message, n_results=2)

    # Build system prompt with mood context and RAG
    system_content = KAI_SYSTEM_PROMPT
    if mood and mood in MOOD_CONTEXT:
        system_content += f"\n\nMood context: {MOOD_CONTEXT[mood]}"
    if rag_context:
        system_content += f"\n\nRelevant knowledge base context (use when helpful, don't quote directly):\n{rag_context}"

    # Build message history (cap at 12 turns)
    messages = [SystemMessage(content=system_content)]
    for turn in history[-12:]:
        if turn.get("role") == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn.get("role") == "assistant":
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=message))

    llm = ChatGroq(
        model=settings.groq_model,
        temperature=0.8,
        max_tokens=350,
        api_key=settings.groq_api_key,
    )

    try:
        response = llm.invoke(messages)
        return response.content.strip(), source_ids
    except Exception as e:
        logger.error(f"Kai response failed: {e}")
        return (
            "I'm here with you. Something went wrong on my end — could you try sending your message again?",
            [],
        )
