"""Processor protocol and shared helpers."""

from __future__ import annotations

from typing import Protocol

from dllinjector.handlers.dll_handler import DllFacts
from dllinjector.handlers.process_handler import ProcessSnapshot
from dllinjector.models.config_model import ConfigModel
from dllinjector.models.job_model import Job, StageResult


class Processor(Protocol):
    """A single safety check. Must not perform injection."""

    name: str

    def run(
        self,
        job: Job,
        snapshot: ProcessSnapshot | None,
        dll: DllFacts,
        config: ConfigModel,
    ) -> StageResult: ...


def pass_result(name: str, **detail: object) -> StageResult:
    return StageResult(stage=name, outcome="pass", detail=dict(detail))


def fail_result(name: str, reason: str, **detail: object) -> StageResult:
    return StageResult(stage=name, outcome="fail", reason=reason, detail=dict(detail))