"""Workflow orchestration: synopsis → title → description → story → thumbnail."""

import os
import sys
import tempfile
from collections.abc import Callable

from openai import OpenAI

from .api import generate_text, generate_youtube_thumbnail, thumbnail_has_visible_text
from .config import AppConfig
from .output_bundle import write_run_bundle
from .prompts import (
    build_description_prompt,
    build_instructions,
    build_synopsis_prompt,
    build_thumbnail_prompt,
    build_title_prompt,
)
from .schemas import ApprovedPipelineBundle, StoryParameters, WorkflowJSONResult
from .story import generate_story_with_guardrails

ApprovalCallback = Callable[[str], bool]
"""Signature: (generated_text) -> True to approve, False to regenerate."""


def approval_loop(
    label: str,
    client: OpenAI,
    instructions: str,
    build_prompt: Callable[[], str],
    approve_fn: ApprovalCallback,
    *,
    model: str,
    purpose: str,
) -> str:
    """Generate text in a loop until *approve_fn* returns ``True``.

    Args:
        label: Step header printed to stderr (e.g. ``"Step 1: Synopsis"``).
        approve_fn: Called with the generated text; return ``True`` to accept.
        purpose: Shown in stderr after the model id for this step (e.g. ``"synopsis"``).
    """
    while True:
        print(f"\n--- {label} ---\n", file=sys.stderr)
        text = generate_text(
            client,
            instructions,
            build_prompt(),
            model=model,
            purpose=purpose,
        )
        print(text, file=sys.stderr)
        print(file=sys.stderr)
        if approve_fn(text):
            return text


def run_workflow(
    client: OpenAI,
    cfg: AppConfig,
    params: StoryParameters,
    approve_fn: ApprovalCallback,
) -> WorkflowJSONResult:
    """Run the full pipeline and write the output bundle.

    Args:
        client: Authenticated OpenAI client.
        cfg: Resolved application configuration.
        params: Validated user inputs.
        approve_fn: Interactive or programmatic approval callback.

    Returns:
        JSON-serializable result (use ``model_dump_json()`` in the caller).
    """
    instructions = build_instructions(params.genre)

    synopsis = approval_loop(
        "Step 1: Synopsis",
        client,
        instructions,
        lambda: build_synopsis_prompt(params),
        approve_fn,
        model=cfg.model_synopsis,
        purpose="synopsis",
    )

    title = approval_loop(
        "Step 2: Video title",
        client,
        instructions,
        lambda: build_title_prompt(synopsis),
        approve_fn,
        model=cfg.model_title,
        purpose="video title",
    )

    description = approval_loop(
        "Step 3: Video description",
        client,
        instructions,
        lambda: build_description_prompt(synopsis, title),
        approve_fn,
        model=cfg.model_description,
        purpose="video description",
    )

    approved = ApprovedPipelineBundle(
        synopsis=synopsis,
        title=title,
        description=description,
    )
    story = generate_story_with_guardrails(
        client, cfg, instructions, params, approved
    )

    thumbnail_path: str | None = None
    tmp_thumb: str | None = None
    print("\n--- YouTube thumbnail (Images API) ---\n", file=sys.stderr, flush=True)
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_thumb = tmp.name
        tmp.close()
        base_thumbnail_prompt = build_thumbnail_prompt(
            title, description, params.genre, params.age_group
        )
        text_detected_across_attempts = False
        max_thumbnail_attempts = cfg.max_thumbnail_gen
        for attempt in range(1, max_thumbnail_attempts + 1):
            if attempt > 1:
                print(
                    f"Thumbnail attempt {attempt}/{max_thumbnail_attempts} "
                    "(retry due to detected text in prior attempt).",
                    file=sys.stderr,
                    flush=True,
                )
            prompt = base_thumbnail_prompt
            if attempt > 1:
                prompt += (
                    "\n\nRetry note: the previous image still contained text. "
                    "Remove all letters, words, numbers, logos with readable characters, "
                    "labels, signs, and watermarks. Use pure illustration with no typography."
                )
            thumbnail_path = generate_youtube_thumbnail(
                client,
                prompt=prompt,
                model=cfg.model_thumbnail_image,
                size=cfg.thumbnail_size,
                output_path=tmp_thumb,
                quality=cfg.thumbnail_quality,
            )
            has_text = thumbnail_has_visible_text(
                client,
                image_path=thumbnail_path,
                model=cfg.model_thumbnail_text_check,
                purpose=f"thumbnail text check (attempt {attempt})",
            )
            if has_text is False:
                break
            if has_text is None:
                # If a text-check model is unavailable, keep the image and do not loop forever.
                break
            text_detected_across_attempts = True
            if attempt == max_thumbnail_attempts:
                break
        if text_detected_across_attempts and thumbnail_path:
            print(
                "Warning: thumbnail text was detected in generated attempts; using last generated image.",
                file=sys.stderr,
                flush=True,
            )
    except Exception as exc:
        print(f"Thumbnail generation failed: {exc}", file=sys.stderr, flush=True)
        thumbnail_path = None

    try:
        bundle_dir = write_run_bundle(
            output_dir=cfg.output_dir,
            title=title,
            description=description,
            story=story,
            thumbnail_source_path=thumbnail_path,
        )
    finally:
        if tmp_thumb:
            try:
                os.unlink(tmp_thumb)
            except OSError:
                pass
    story_md = bundle_dir / "STORY.md"
    thumb = bundle_dir / "thumbnail.png"
    print(f"Bundle directory: {bundle_dir}", file=sys.stderr, flush=True)

    return WorkflowJSONResult(
        title=title,
        description=description,
        story=story,
        story_md_path=str(story_md.resolve()),
        thumbnail_path=str(thumb.resolve()) if thumb.is_file() else None,
    )
