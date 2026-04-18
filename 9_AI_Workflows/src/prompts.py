"""Instruction and user-prompt strings for the story workflow."""

from __future__ import annotations

import re
import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schemas import ApprovedPipelineBundle, StoryParameters


def get_model_role(genre: str) -> str:
    """Return the one-line model role for Responses API instructions.

    Args:
        genre: User-provided genre; normalized for wording. If blank after
            stripping, uses 'fiction'.

    Returns:
        A single sentence describing the model role for this run.
    """
    genre_label = " ".join(genre.split()).strip() or "fiction"
    return f"You are a short-form {genre_label} generator for video narration."


def get_guardrails() -> str:
    """Return safety and style policy text (excluding the role line).

    Covers universal safety rules, age-band guidance, genre adaptation, and
    output-shape rules. Combine with get_model_role via build_instructions.

    Returns:
        Multi-line instruction text for the instructions field.
    """
    return textwrap.dedent(
        """
        Safety (all requests, all age groups):
        - No sexual content or innuendo.
        - No profanity, slurs, or hateful content.
        - No violence: no physical fights, weapons, injury, gore, death, or
          glorification of harm. Use non-violent conflict (feelings, choices,
          obstacles) and age-appropriate mild peril only—no scary or graphic detail.

        Age group (use the age group given in the user message):
        - Children: simple vocabulary, gentle themes, reassuring tone.
        - Teens: more emotional complexity and stakes; still follow all safety rules.
        - Young adult: richer language and themes; still follow all safety rules.

        Genre: If the requested genre would require violence or explicit content,
        adapt to a family-friendly version of that mood (e.g. cozy mystery,
        light adventure) instead of refusing unless impossible.

        Output: Follow the user message for this step. Return only what was asked
        for—no preambles, labels, or meta commentary unless the user message says otherwise.
        Use plain text only: no hashtags and no emojis in any output.
        """
    ).strip()


def get_thumbnail_image_guardrails() -> str:
    """Safety rules for generated thumbnail images (Images API prompt text).

    Aligned with story guardrails: no explicit content, no violence, family-friendly visuals.
    """
    return textwrap.dedent(
        """
        Image guardrails (must all be satisfied):
        - No sexual content, nudity, or explicit imagery.
        - No violence: no fights, weapons, blood, gore, injury, death, or horror imagery.
        - No hateful, discriminatory, or illegal symbols or scenes.
        - No scary or graphic detail; keep mood age-appropriate and reassuring for the audience.
        - If the topic could imply violence, show a gentle, non-violent interpretation only.
        - Eye-catching composition, readable at small preview size; strong focal subject.
        - ABSOLUTELY NO TEXT in the image: no letters, words, numbers, captions, titles, labels, logos,
          watermarks, signs, book covers with readable type, UI chrome, or any typography whatsoever.
          Pure illustration only—not a single character of text anywhere in the image.
        - No hashtags or emojis in the image.
        """
    ).strip()


def _word_match(pattern: str, text: str) -> bool:
    """Check for a whole-word (word-boundary) match of *pattern* in *text*."""
    return re.search(rf"\b{re.escape(pattern)}\b", text) is not None


def _thumbnail_cartoon_style_instruction(age_group: str) -> str:
    """Cartoon / illustrated look tuned from the user's age_group string."""
    s = " ".join(age_group.split()).strip().lower()
    if not s:
        return (
            "Visual style: cheerful cartoon illustration—clear shapes, expressive, not photorealistic."
        )
    if any(
        _word_match(k, s)
        for k in (
            "toddler",
            "preschool",
            "children",
            "child",
            "kid",
            "kids",
            "elementary",
        )
    ):
        return (
            "Visual style: bright, playful cartoon (rounded shapes, friendly storybook illustration)—"
            "suited to young children; not photorealistic."
        )
    if any(
        _word_match(k, s)
        for k in ("teen", "teens", "adolescent", "middle school", "high school")
    ):
        return (
            "Visual style: bold stylized cartoon or semi-cartoon (animated-series feel)—suited to teens; "
            "not photorealistic."
        )
    if _word_match("young adult", s) or s == "ya":
        return (
            "Visual style: polished cartoon or illustrated look with expressive exaggeration—suited to "
            "young adult viewers; not photorealistic, still family-friendly."
        )
    if _word_match("adult", s) or _word_match("adults", s):
        return (
            "Visual style: polished cartoon or illustrated look—suited to adult viewers; not photorealistic, "
            "still family-friendly."
        )
    return (
        "Visual style: cartoonish illustrated scene—clear focal subject, expressive, not photorealistic, "
        "appropriate for the stated audience."
    )


def build_instructions(genre: str) -> str:
    """Build the full Responses API instructions string (role plus guardrails).

    Args:
        genre: Passed to get_model_role for the opening persona line.

    Returns:
        Text suitable for the instructions parameter on responses.create.
    """
    return f"""{get_model_role(genre)}

{get_guardrails()}"""


def build_synopsis_prompt(params: "StoryParameters") -> str:
    """Build the user message for step 1 (brief synopsis).

    Args:
        params: Validated story parameters from the CLI.

    Returns:
        User input string for the Responses API (not the instructions field).
    """
    focus = params.subject or "the chosen topic"
    return f"""Write a brief synopsis (2–4 sentences) for a video narration story.

Parameters:
- Subject / focus: {focus}
- Genre: {params.genre}
- Age group: {params.age_group}
- Target video length: about {params.video_length} minutes (read-aloud pacing)

Return only the synopsis."""


def build_title_prompt(synopsis: str) -> str:
    """Build the user message for step 2 (video title from synopsis).

    Args:
        synopsis: Approved synopsis text from step 1.

    Returns:
        User input string for the Responses API.
    """
    return f"""Approved synopsis:

{synopsis}

Write one short, compelling video title. Return only the title (plain text, no quotation marks)."""


def build_description_prompt(synopsis: str, title: str) -> str:
    """Build the user message for step 3 (video description).

    Args:
        synopsis: Approved synopsis text.
        title: Approved title from step 2.

    Returns:
        User input string for the Responses API.
    """
    return f"""Synopsis:

{synopsis}

Video title:

{title}

Write a concise video description (1–2 short paragraphs) suitable for a platform like YouTube—engaging and faithful to the synopsis. Return only the description."""


def build_thumbnail_prompt(
    title: str,
    description: str,
    genre: str,
    age_group: str,
) -> str:
    """Prompt for Images API: YouTube thumbnail from title + description and guardrails."""
    genre_label = " ".join(genre.split()).strip() or "general audience"
    audience = " ".join(age_group.split()).strip() or "general audience"
    content = f"{title.strip()}: {description.strip()}"
    cartoon = _thumbnail_cartoon_style_instruction(age_group)
    guardrails = get_thumbnail_image_guardrails()
    return f"""Create a single wide landscape image suitable as a YouTube thumbnail.

CRITICAL: The image must contain absolutely NO text, NO hashtags, and NO emojis. Zero letters, words, numbers, captions, titles, labels, logos, watermarks, signs, or typographic elements of any kind. Pure illustration only.

Video content (use for mood and subject only—do NOT render any of this as text in the image):
{content}

Genre / tone: {genre_label}
Intended audience: {audience}

{cartoon}

{guardrails}"""


def build_full_story_prompt(
    params: "StoryParameters",
    approved: "ApprovedPipelineBundle",
    *,
    revision_note: str | None = None,
) -> str:
    """Build the user message for step 4 (full narration; no post-approval).

    Args:
        params: Original story parameters.
        approved: User-approved synopsis, title, and description.
        revision_note: If set, appended as guidance after a failed guardrails check.

    Returns:
        User input string for the Responses API.
    """
    focus = params.subject or "the chosen topic"
    base = f"""Write the full narration / story text for the video. Expand the approved synopsis into the complete script; stay consistent with the title and description.

Approved synopsis:
{approved.synopsis}

Approved title:
{approved.title}

Approved description:
{approved.description}

Original parameters (keep tone and length appropriate):
- Subject / focus: {focus}
- Genre: {params.genre}
- Age group: {params.age_group}
- Target length: about {params.video_length} minutes when read aloud.

Return only the story body."""
    if revision_note:
        base = base.rstrip() + (
            "\n\nThe previous draft failed an automated guardrails check. "
            f"Revise the full story to address this: {revision_note}\n"
            "Return only the revised story body."
        )
    return base


def get_checker_instructions() -> str:
    """Instructions for the guardrails-only review (output shape is enforced by the API)."""
    return (
        "You are a lightweight compliance checker for video narration scripts. "
        "Judge only against the guardrails and story in the user message."
    )


def build_guardrails_check_prompt(guardrails: str, story: str) -> str:
    """User message for PASS/FAIL review of story text against guardrails."""
    return f"""These GUARDRAILS must all be satisfied:

{guardrails}

---

STORY TO CHECK:

{story}

---

Decide whether the story satisfies every guardrail; the response fields are fixed by the API schema."""
