"""Verify the DLL's Authenticode signature against trusted publishers."""

from __future__ import annotations

from dllinjector.handlers.dll_handler import DllFacts
from dllinjector.handlers.process_handler import ProcessSnapshot
from dllinjector.models.config_model import ConfigModel
from dllinjector.models.job_model import Job, StageResult
from dllinjector.processors.base import fail_result, pass_result

NAME = "dll_signature"


def run(
    job: Job,
    snapshot: ProcessSnapshot | None,
    dll: DllFacts,
    config: ConfigModel,
) -> StageResult:
    section = config.processors.dll_signature
    if not section.enabled:
        return pass_result(NAME, skipped=True)

    if not dll.has_signature:
        if section.require_signed:
            return fail_result(NAME, "dll is unsigned and require_signed=true")
        return pass_result(NAME, signed=False, enforced=False)

    signer = dll.signer or ""
    if section.trusted_publishers and not any(p in signer for p in section.trusted_publishers):
        return fail_result(NAME, f"signer not trusted: {signer!r}")

    return pass_result(NAME, signed=True, signer=signer)