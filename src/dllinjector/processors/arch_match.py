"""Reject injections where the DLL architecture doesn't match the target."""

from __future__ import annotations

from dllinjector.handlers.dll_handler import DllFacts
from dllinjector.handlers.process_handler import ProcessSnapshot
from dllinjector.models.config_model import ConfigModel
from dllinjector.models.job_model import Job, StageResult
from dllinjector.processors.base import fail_result, pass_result

NAME = "arch_match"


def run(
    job: Job,
    snapshot: ProcessSnapshot | None,
    dll: DllFacts,
    config: ConfigModel,
) -> StageResult:
    if snapshot is None:
        return fail_result(NAME, "no process snapshot available")
    if not config.processors.arch_match.enabled:
        return pass_result(NAME, skipped=True)

    target_arch = snapshot.arch
    dll_arch = dll.machine

    if target_arch is None or dll_arch is None:
        return fail_result(NAME, "could not determine architecture", target=target_arch, dll=dll_arch)

    if target_arch == dll_arch:
        return pass_result(NAME, arch=target_arch)

    # x86 DLL into x64 process is never valid. WOW64 bridge is the only
    # case where a mismatch is technically injectable, and only when the
    # config explicitly allows it.
    if config.processors.arch_match.allow_wow64_bridge and {target_arch, dll_arch} == {"x64", "x86"}:
        return pass_result(NAME, arch=target_arch, wow64_bridge=True)

    return fail_result(NAME, f"arch mismatch: target={target_arch} dll={dll_arch}")