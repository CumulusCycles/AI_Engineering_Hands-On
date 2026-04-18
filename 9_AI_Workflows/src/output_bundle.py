"""Write completed run artifacts under the configured output directory."""

from __future__ import annotations

import re
import shutil
from datetime import datetime
from pathlib import Path


def resolve_output_dir(output_dir: str) -> Path:
    """Resolve *output_dir* (from config) to an absolute ``Path``."""
    p = Path(output_dir)
    return p if p.is_absolute() else Path.cwd() / p


def sanitize_title_for_folder(title: str) -> str:
    slug = title.strip().lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "_", slug).strip("_")
    return slug[:80] if slug else "untitled"


def build_run_folder_name(title: str, when: datetime | None = None) -> str:
    """``{sanitized_title}_{MM-DD-YYYY}`` (slashes not used — invalid in paths)."""
    d = (when or datetime.now()).strftime("%m-%d-%Y")
    return f"{sanitize_title_for_folder(title)}_{d}"


_MAX_SUFFIX = 1000


def _unique_run_dir(base: Path, folder_name: str) -> Path:
    dest = base / folder_name
    if not dest.exists():
        return dest
    for n in range(2, _MAX_SUFFIX + 1):
        alt = base / f"{folder_name}_{n}"
        if not alt.exists():
            return alt
    raise RuntimeError(
        f"Could not create a unique run directory under {base} "
        f"for '{folder_name}' after {_MAX_SUFFIX} attempts"
    )


def _write_story_md(path: Path, title: str, description: str, story: str) -> None:
    body = f"""# Title

{title}

# Description

{description}

# Story

{story}
"""
    path.write_text(body, encoding="utf-8")


def write_run_bundle(
    *,
    output_dir: str,
    title: str,
    description: str,
    story: str,
    thumbnail_source_path: str | None,
) -> Path:
    """Create ``<output_dir>/<title>_<date>/`` with ``STORY.md`` and ``thumbnail.png``.

    Returns the resolved run directory path.
    """
    base = resolve_output_dir(output_dir)
    base.mkdir(parents=True, exist_ok=True)
    folder_name = build_run_folder_name(title)
    run_dir = _unique_run_dir(base, folder_name)
    run_dir.mkdir(parents=True)

    _write_story_md(run_dir / "STORY.md", title, description, story)

    if thumbnail_source_path:
        src = Path(thumbnail_source_path)
        if src.is_file():
            shutil.copy2(src, run_dir / "thumbnail.png")

    return run_dir.resolve()
