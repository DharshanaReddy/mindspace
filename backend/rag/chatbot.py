"""
Kai — RAG-powered mental health support chatbot.
Uses LangChain + ChromaDB for grounded, evidence-based responses.
Every conversation traced with LangSmith.
"""

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langsmith import traceable
import logging
from .vectorstore import retrieve_mental_health_context
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

KAI_SYSTEM_PROMPT = """You are Kai, a compassionate AI mental health companion on MindSpace.

Your character:
- Warm, empathetic, and non-judgmental — you hold space without rushing to fix
- Evidence-informed: you draw on psychology and CBT when helpful, but never diagnose
- Honest: you acknowledge when something is beyond your scope and encourage professional help
- Concise: 2-4 sentences usually — quality over length

What you do:
- Actively listen and validate emotions
- Ask one thoughtful clarifying question at a time
- Offer grounding techniques, breathing exercises, or reframing when appropriate
- Remind users they are not alone

What you never do:
- Diagnose or prescribe
- Give toxic positivity ("just think positive!")
- Replace a licensed therapist

Crisis protocol: If someone expresses thoughts of self-harm or suicide, respond with care and
provide the 988 Suicide & Crisis Lifeline (call or text 988 in the US).

Grounding in knowledge: You have access to evidence-based mental health resources.
When relevant, weave in specific techniques from this context — don't just paraphrase generically."""

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

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0.8,
        max_tokens=350,
        api_key=settings.openai_api_key,
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
