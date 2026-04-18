"""Full story generation with guardrails check and bounded retries."""

import sys

from openai import OpenAI

from .api import generate_text, guardrails_check
from .config import AppConfig
from .exceptions import GuardrailsViolation
from .prompts import build_full_story_prompt, build_guardrails_check_prompt, get_checker_instructions, get_guardrails
from .schemas import ApprovedPipelineBundle, StoryParameters


def generate_story_with_guardrails(
    client: OpenAI,
    cfg: AppConfig,
    instructions: str,
    params: StoryParameters,
    approved: ApprovedPipelineBundle,
) -> str:
    """Generate the narration story; re-run on guard failure up to ``cfg.max_story_gen`` times.

    Raises ``GuardrailsViolation`` if every draft fails the check.
    """
    max_gen = cfg.max_story_gen
    last_fail_reason = ""
    story = ""
    print(
        f"Full story: up to {max_gen} draft(s) if the guardrails check fails "
        f"(each draft = story text, then check).",
        file=sys.stderr,
        flush=True,
    )
    for attempt in range(1, max_gen + 1):
        if attempt == 1:
            print(
                f"Full story: draft 1 of {max_gen}",
                file=sys.stderr,
                flush=True,
            )
        else:
            print(
                f"Full story: draft {attempt} of {max_gen} — NEW DRAFT because draft "
                f"{attempt - 1} failed the guardrails check",
                file=sys.stderr,
                flush=True,
            )
        story = generate_text(
            client,
            instructions,
            build_full_story_prompt(
                params,
                approved,
                revision_note=last_fail_reason or None,
            ),
            model=cfg.model_story,
            purpose="full story text",
        )
        ok, fail_reason = guardrails_check(
            client,
            get_checker_instructions(),
            build_guardrails_check_prompt(get_guardrails(), story),
            model=cfg.model_story_guard,
        )
        if ok:
            print("Guardrails check passed.", file=sys.stderr, flush=True)
            break
        last_fail_reason = fail_reason
        if attempt < max_gen:
            print(
                f"Guardrails check FAILED for draft {attempt} of {max_gen}. "
                f"Will run draft {attempt + 1} of {max_gen} next (story regenerated with failure feedback).",
                file=sys.stderr,
                flush=True,
            )
        else:
            raise GuardrailsViolation(
                f"Story failed the guardrails check after {max_gen} draft(s): "
                f"{fail_reason or 'unspecified'}"
            )
    return story
