"""
Mood and sentiment analysis using OpenAI GPT-4o-mini.
Detects one of 8 emotional states + sentiment polarity from free-form text.
This approach leverages prompt engineering for nuanced mood classification —
more accurate than lexicon-based methods for mental health contexts.
"""

import json
import logging
from openai import AsyncOpenAI
from langsmith import traceable
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

MOODS = ["Happy", "Sad", "Anxious", "Angry", "Lonely", "Stressed", "Hopeful", "Exhausted"]

SYSTEM_PROMPT = """You are a clinical-grade mood analysis system trained on mental health literature.
Analyze the emotional content of text and classify it with high precision.
Always respond with valid JSON only."""

ANALYSIS_PROMPT = """Analyze the emotional state expressed in this text:

"{text}"

Classify using these 8 mood categories: {moods}

Return JSON:
{{
  "detected_mood": "<one of the 8 moods>",
  "confidence": <0.0-1.0>,
  "sentiment": "<positive|negative|neutral|mixed>",
  "emotional_intensity": "<low|moderate|high>",
  "explanation": "<one sentence explaining the classification>",
  "secondary_mood": "<optional second mood if present, else null>"
}}"""


@traceable(name="mood-sentiment-analysis")
async def analyze_mood(text: str) -> dict:
    """
    Classify mood and sentiment from free-form text using GPT-4o-mini.
    Returns structured analysis with confidence score.
    """
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": ANALYSIS_PROMPT.format(text=text[:500], moods=", ".join(MOODS)),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=200,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.warning(f"Mood analysis failed: {e}")
        return {
            "detected_mood": "Stressed",
            "confidence": 0.5,
            "sentiment": "neutral",
            "emotional_intensity": "moderate",
            "explanation": "Analysis unavailable",
            "secondary_mood": None,
        }
