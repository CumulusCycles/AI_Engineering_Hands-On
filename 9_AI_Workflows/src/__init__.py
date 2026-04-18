"""Video narration workflow package (synopsis, title, description, story)."""

from importlib.metadata import PackageNotFoundError, version

from .config import AppConfig
from .exceptions import GuardrailsViolation, UserQuit
from .schemas import StoryParameters, WorkflowJSONResult
from .workflow import run_workflow

try:
    __version__ = version("video-content-generator")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__all__ = [
    "__version__",
    "AppConfig",
    "GuardrailsViolation",
    "StoryParameters",
    "UserQuit",
    "WorkflowJSONResult",
    "run_workflow",
]
