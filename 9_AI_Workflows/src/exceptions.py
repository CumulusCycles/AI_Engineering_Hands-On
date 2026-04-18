"""Application-level exceptions."""


class UserQuit(Exception):
    """Raised when the user chooses to quit the interactive CLI."""


class GuardrailsViolation(Exception):
    """Raised when no generated story draft satisfies the configured guardrails."""
