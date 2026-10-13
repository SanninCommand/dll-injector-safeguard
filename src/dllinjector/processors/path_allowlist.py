"""Enforce that the DLL lives under a user-approved root.

The allowlist is empty by default — nothing injects until the user
opts in. Symlinks and junctions are resolved before comparison so
`C:\\tmp\\evil.lnk -> C:\\Windows\\System32\\kernel32.dll` doesn't sneak
through.
"""

from __future__ import annotations

from pathlib import Path

from dllinjector.handlers.dll_handler import DllFacts
from dllinjector.handlers.process_handler import ProcessSnapshot
from dllinjector.models.config_model import ConfigModel
from dllinjector.models.job_model import Job, StageResult
from dllinjector.processors.base import fail_result, pass_result
from dllinjector.utils.paths import is_under_any, is_unc

NAME = "path_allowlist"


def run(
    job: Job,
    snapshot: ProcessSnapshot | None,
    dll: DllFacts,
    config: ConfigModel,
) -> StageResult:
    section = config.processors.path_allowlist
    if not section.enabled:
        return pass_result(NAME, skipped=True)

    candidate = dll.path.resolve() if section.resolve_symlinks else dll.path

    if section.reject_unc and is_unc(candidate):
        return fail_result(NAME, f"UNC path rejected: {candidate}")

    if not section.allowed_roots:
        return fail_result(NAME, "allowlist is empty — add a root to config")

    if not is_under_any(candidate, section.allowed_roots):
        return fail_result(NAME, f"dll outside allowlist: {candidate}")

    return pass_result(NAME, allowed_roots=[str(p) for p in section.allowed_roots])