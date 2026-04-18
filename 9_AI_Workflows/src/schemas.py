"""Pydantic models for workflow inputs, guardrails output, and final artifacts."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StoryParameters(BaseModel):
    """
    User-provided inputs collected at the start of the CLI run.

    Attributes:
        subject (str): Main topic or focus for the video narration (e.g. a character or setting).
        genre (str): Genre or tone for the story (e.g. adventure, cozy mystery).
        age_group (str): Intended audience age band or label (e.g. children, teens).
        video_length (int): Target video length in minutes.
    """

    model_config = ConfigDict(extra="forbid")

    subject: str = Field(
        ...,
        description="Main topic or focus for the video narration (e.g. a character or setting).",
    )
    genre: str = Field(
        ...,
        description="Genre or tone for the story (e.g. adventure, cozy mystery).",
    )
    age_group: str = Field(
        ...,
        description="Intended audience age band or label (e.g. children, teens).",
    )
    video_length: int = Field(
        ...,
        gt=0,
        description="Target video length in minutes.",
    )

    @field_validator("video_length", mode="before")
    @classmethod
    def _coerce_video_length(cls, v: object) -> int:
        """Accept string input from the CLI and convert to int."""
        if isinstance(v, str):
            return int(v)
        return v  # type: ignore[return-value]


class ApprovedPipelineBundle(BaseModel):
    """
    Approved synopsis, title, and description before full-story generation.

    Attributes:
        synopsis (str): User-approved short synopsis from step 1.
        title (str): User-approved video title from step 2.
        description (str): User-approved video description from step 3.
    """

    model_config = ConfigDict(extra="forbid")

    synopsis: str = Field(
        ...,
        description="User-approved short synopsis from step 1.",
    )
    title: str = Field(
        ...,
        description="User-approved video title from step 2.",
    )
    description: str = Field(
        ...,
        description="User-approved video description from step 3.",
    )


class GuardrailsCheckResult(BaseModel):
    """
    Structured output from the post-story guardrails review (OpenAI JSON schema).

    Attributes:
        passed (bool): True if the story text fully satisfies every listed guardrail; false if any rule is violated.
        failure_reason (str): If passed is false: one short sentence listing concrete violations. If passed is true: must be an empty string.
    """

    model_config = ConfigDict(extra="forbid")

    passed: bool = Field(
        ...,
        description=(
            "True only if the story text fully satisfies every listed guardrail; "
            "false if any rule is violated."
        ),
    )
    failure_reason: str = Field(
        default="",
        description=(
            "If passed is false: one short sentence listing concrete violations. "
            "If passed is true: must be an empty string."
        ),
    )


class WorkflowJSONResult(BaseModel):
    """
    Terminal / API response payload after a successful run.

    Attributes:
        title (str): Video title.
        description (str): Video description.
        story (str): Full story text.
        story_md_path (str): Absolute path to the written STORY.md file.
        thumbnail_path (str | None): Absolute path to thumbnail.png in the bundle, if present.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., description="Video title.")
    description: str = Field(..., description="Video description.")
    story: str = Field(..., description="Full story text.")
    story_md_path: str = Field(
        ...,
        description="Absolute path to the written STORY.md file.",
    )
    thumbnail_path: str | None = Field(
        default=None,
        description="Absolute path to thumbnail.png in the bundle, if present.",
    )
