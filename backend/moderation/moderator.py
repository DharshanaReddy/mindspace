"""
Content moderation using OpenAI Moderation API.
Screens posts before they go live to ensure community safety.
"""

from openai import AsyncOpenAI
import logging
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ModerationResult:
    def __init__(self, flagged: bool, categories: dict, reason: str = ""):
        self.flagged = flagged
        self.categories = categories
        self.reason = reason


async def moderate_content(text: str) -> ModerationResult:
    """
    Screen content through OpenAI's moderation endpoint.
    Returns structured result with flag status and triggered categories.
    """
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    try:
        response = await client.moderations.create(
            model=settings.openai_moderation_model,
            input=text,
        )
        result = response.results[0]
        flagged_cats = {
            cat: score
            for cat, score in result.category_scores.__dict__.items()
            if score > 0.5
        }
        reason = ", ".join(flagged_cats.keys()) if flagged_cats else ""
        return ModerationResult(
            flagged=result.flagged,
            categories=flagged_cats,
            reason=reason,
        )
    except Exception as e:
        logger.warning(f"Moderation API failed: {e}. Allowing content through.")
        return ModerationResult(flagged=False, categories={})
