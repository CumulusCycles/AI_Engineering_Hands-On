"""CLI entry point: interactive terminal I/O and workflow invocation."""

import sys

from openai import APIError

from .api import create_client
from .config import AppConfig
from .exceptions import GuardrailsViolation, UserQuit
from .schemas import StoryParameters
from .workflow import run_workflow


def _read_line(prompt: str) -> str:
    """Read one stripped line from stdin, raising ``UserQuit`` on quit/signal."""
    try:
        value = input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        raise UserQuit("Goodbye.")
    if value.lower() in ("q", "quit", "exit"):
        raise UserQuit("Goodbye.")
    return value


def _require_input(prompt: str) -> str:
    """Loop ``_read_line`` until a non-empty value is provided."""
    while True:
        value = _read_line(prompt)
        if value:
            return value
        print("  (required — please enter a value)", file=sys.stderr)


def _get_story_parameters() -> StoryParameters:
    """Prompt for subject, genre, age group, and target video length."""
    print("Enter parameters (q / quit / exit at any prompt to stop).\n", file=sys.stderr)
    subject = _require_input("Subject (e.g. a unicorn): ")
    genre = _require_input("Genre: ")
    age_group = _require_input("Age group: ")
    while True:
        raw_length = _require_input(
            "Video length in minutes, 3-5 (number only, e.g. 4): "
        )
        try:
            return StoryParameters(
                subject=subject,
                genre=genre,
                age_group=age_group,
                video_length=raw_length,
            )
        except ValueError:
            print("  (enter a positive whole number)", file=sys.stderr)


def _prompt_approve_regenerate_quit() -> bool:
    """Interactive approval prompt. Returns ``True`` to approve, ``False`` to regenerate."""
    while True:
        try:
            choice = input(
                "Approve? [y]es accept / [n]o regenerate / [q]uit: "
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            raise UserQuit("Goodbye.")
        if choice in ("y", "yes", "approve", "a"):
            return True
        if choice in ("n", "no", "decline", "d", "r", "regenerate"):
            return False
        if choice in ("q", "quit", "exit"):
            raise UserQuit("Goodbye.")
        print("Please enter y, n, or q.", file=sys.stderr)


def _cli_approve(_text: str) -> bool:
    """Approval callback wired to the interactive terminal prompt."""
    return _prompt_approve_regenerate_quit()


def main() -> None:
    """Run the interactive CLI.

    Status messages go to stderr; the final JSON result goes to stdout so it
    can be piped or parsed by a downstream consumer.
    """
    try:
        cfg = AppConfig.from_env()
        client = create_client()
        params = _get_story_parameters()
        result = run_workflow(client, cfg, params, _cli_approve)
        print(result.model_dump_json(indent=2))
    except UserQuit as exc:
        print(exc, file=sys.stderr)
    except GuardrailsViolation as exc:
        print(f"Guardrails check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except APIError as exc:
        print(f"OpenAI API error: {exc}", file=sys.stderr)
        raise SystemExit(1)
