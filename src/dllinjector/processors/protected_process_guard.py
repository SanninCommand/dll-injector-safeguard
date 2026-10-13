"""Refuse to inject into protected or system-critical processes.

This is the check that keeps someone from pointing the tool at lsass
and getting a bluescreen (or worse). It runs before the driver and
cannot be disabled by CLI flag — only by editing config.
"""

from __future__ import annotations

from dllinjector.handlers.dll_handler import DllFacts
from dllinjector.handlers.process_handler import ProcessSnapshot
from dllinjector.models.config_model import ConfigModel
from dllinjector.models.job_model import Job, StageResult
from dllinjector.processors.base import fail_result, pass_result

NAME = "protected_process_guard"


def run(
    job: Job,
    snapshot: ProcessSnapshot | None,
    dll: DllFacts,
    config: ConfigModel,
) -> StageResult:
    section = config.processors.protected_process_guard
    if not section.enabled:
        return pass_result(NAME, skipped=True)

    if snapshot is None:
        return fail_result(NAME, "no snapshot — cannot verify target")

    name_lower = snapshot.name.lower()
    denied = {n.lower() for n in section.denied_names}
    if name_lower in denied:
        return fail_result(NAME, f"target {snapshot.name} is in the deny list")

    if section.deny_system_processes and snapshot.username in {"NT AUTHORITY\\SYSTEM", "SYSTEM"}:
        return fail_result(NAME, f"target runs as SYSTEM: {snapshot.name}")

    return pass_result(NAME, target=snapshot.name)