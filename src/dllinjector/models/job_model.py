"""Job and PipelineResult models.

A Job is the immutable description of one injection request. A
PipelineResult is what the runner hands back after the safety checks
and (optionally) the driver have run.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class InjectionBackend(str, Enum):
    CREATE_REMOTE_THREAD = "createremotethread"
    QUEUE_USER_APC = "queueuserapc"
    SET_WINDOWS_HOOK_EX = "sethooksex"


class Job(BaseModel):
    """One injection request. Frozen — processors must not mutate it."""

    model_config = {"frozen": True}

    pid: int = Field(gt=0)
    process_name: str
    dll_path: Path
    backend: InjectionBackend
    elevate: bool = False
    dry_run: bool = False
    issued_at: float


class StageOutcome(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


class StageResult(BaseModel):
    """Result of a single pipeline stage."""

    stage: str
    outcome: StageOutcome
    reason: str | None = None
    detail: dict[str, object] = Field(default_factory=dict)


class PipelineResult(BaseModel):
    """Aggregate result of a full pipeline run."""

    ok: bool
    failed_stage: str | None = None
    reason: str | None = None
    stages: list[StageResult] = Field(default_factory=list)
    injection: Literal["performed", "skipped", "failed"] = "skipped"