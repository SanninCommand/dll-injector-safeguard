"""Turn CLI flags into a validated Job.

This module resolves the process spec (name -> PID), canonicalizes the
DLL path, and stamps the job with an issue timestamp. Nothing here
performs injection — it only shapes the request.
"""

from __future__ import annotations

import time
from pathlib import Path

from dllinjector.models.config_model import ConfigModel
from dllinjector.models.job_model import InjectionBackend, Job
from dllinjector.services.process_index import resolve_process_spec
from dllinjector.utils.paths import canonicalize_dll_path


class JobBuildError(RuntimeError):
    """Raised when the CLI inputs cannot be turned into a valid Job."""


def build_job(
    *,
    process_spec: str,
    dll_path: Path,
    backend: str,
    elevate: bool,
    dry_run: bool,
    config: ConfigModel,
) -> Job:
    """Resolve process + DLL and return a Job ready for the pipeline."""
    pid, exe_name = resolve_process_spec(process_spec)
    if pid is None:
        raise JobBuildError(f"no running process matches: {process_spec}")

    canonical = canonicalize_dll_path(dll_path, resolve_symlinks=True)
    if not canonical.exists():
        raise JobBuildError(f"dll path does not exist: {canonical}")

    try:
        backend_enum = InjectionBackend(backend.lower())
    except ValueError as exc:
        raise JobBuildError(f"unknown backend: {backend}") from exc

    if backend_enum.value not in config.drivers.backends:
        raise JobBuildError(f"backend {backend_enum.value} not configured")

    return Job(
        pid=pid,
        process_name=exe_name,
        dll_path=canonical,
        backend=backend_enum,
        elevate=elevate,
        dry_run=dry_run,
        issued_at=time.time(),
    )