"""Prompt engine: loads prompt templates from disk and caches them in memory.

Prompt templates live in ``app/prompts/*.txt``. Templates use ``str.format``
style placeholders (e.g. ``{complaint}``). To keep formatting predictable we
escape any literal braces in the templates ourselves is unnecessary because the
templates only contain the intended placeholders; we therefore use a small
safe-substitution helper instead of ``str.format`` to avoid KeyError on stray
braces in the example JSON.
"""

from __future__ import annotations

import logging
from functools import cache
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


@cache
def load_prompt(name: str) -> str:
    """Load a prompt template by name (without extension) and cache it.

    Args:
        name: The prompt file stem, e.g. ``"analyze"`` for ``analyze.txt``.

    Returns:
        The raw template text.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    logger.debug("Loading prompt template: %s", path)
    return path.read_text(encoding="utf-8")


def render_prompt(name: str, **variables: str) -> str:
    """Render a prompt template by replacing ``{key}`` placeholders.

    A safe replacement is used (simple ``str.replace`` per variable) so that
    literal braces in the template body (such as the example JSON in
    ``analyze.txt``) are left untouched.

    Args:
        name: Prompt file stem.
        **variables: Placeholder values to substitute.

    Returns:
        The rendered prompt string.
    """
    template = load_prompt(name)
    rendered = template
    for key, value in variables.items():
        rendered = rendered.replace(f"{{{key}}}", value)
    return rendered


def get_analyze_prompt(complaint: str) -> str:
    """Return the fully rendered analyze prompt for a complaint."""
    return render_prompt("analyze", complaint=complaint)


def get_letter_prompt(complaint: str, analysis: str) -> str:
    """Return the fully rendered letter prompt for a complaint + analysis."""
    return render_prompt("letter", complaint=complaint, analysis=analysis)


def warm_cache() -> None:
    """Pre-load known prompts into the cache (used at startup)."""
    for name in ("analyze", "letter"):
        load_prompt(name)
    logger.info("Prompt cache warmed: %s", ", ".join(("analyze", "letter")))
