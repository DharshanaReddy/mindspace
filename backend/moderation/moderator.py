"""
Content moderation using keyword-based filtering.
Screens posts before they go live to ensure community safety.
"""

import logging

logger = logging.getLogger(__name__)

FLAGGED_PATTERNS = [
    "kill yourself", "kys", "end your life", "you should die",
    "go kill", "hurt yourself", "self harm", "commit suicide",
]


class ModerationResult:
    def __init__(self, flagged: bool, categories: dict, reason: str = ""):
        self.flagged = flagged
        self.categories = categories
        self.reason = reason


async def moderate_content(text: str) -> ModerationResult:
    """
    Screen content for harmful patterns.
    Flags content that promotes self-harm or targeted harassment.
    """
    text_lower = text.lower()
    for pattern in FLAGGED_PATTERNS:
        if pattern in text_lower:
            return ModerationResult(
                flagged=True,
                categories={"self-harm": 1.0},
                reason=f"Content matches restricted pattern",
            )
    return ModerationResult(flagged=False, categories={})
