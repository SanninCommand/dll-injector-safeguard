"""Resolve a process spec into a live snapshot.

Handlers don't decide anything — they gather facts and hand them to
processors. This one builds a ProcessSnapshot the pipeline can trust
for the duration of a single run.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import psutil

from dllinjector.services.telemetry import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class ProcessSnapshot:
    """Live view of the target process at snapshot time."""

    pid: int
    name: str
    exe: str | None
    arch: str | None
    parent_pid: int | None
    username: str | None
    captured_at: float = field(default_factory=time.time)
    is_protected: bool = False


def snapshot_process(pid: int) -> ProcessSnapshot | None:
    """Return a ProcessSnapshot for `pid`, or None if it's gone."""
    try:
        proc = psutil.Process(pid)
        with proc.oneshot():
            name = proc.name()
            exe = _safe(proc.exe)
            ppid = proc.ppid()
            user = _safe(lambda: proc.username())
    except psutil.NoSuchProcess:
        log.info("target process gone before snapshot", extra={"pid": pid})
        return None
    except psutil.AccessDenied:
        # Access denied on exe/username is common for other users' procs.
        log.warning("partial snapshot — access denied", extra={"pid": pid})
        return ProcessSnapshot(
            pid=pid, name="<denied>", exe=None, arch=None, parent_pid=None, username=None
        )

    arch = _infer_arch(exe)
    return ProcessSnapshot(
        pid=pid,
        name=name,
        exe=exe,
        arch=arch,
        parent_pid=ppid,
        username=user,
    )


def _safe(fn):
    try:
        return fn()
    except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
        return None


def _infer_arch(exe: str | None) -> str | None:
    """Infer PE architecture from the exe header. Returns 'x64'/'x86'/None."""
    if not exe:
        return None
    try:
        import pefile

        pe = pefile.PE(exe, fast_load=True)
        machine = pe.FILE_HEADER.Machine
        pe.close()
        if machine == 0x8664:
            return "x64"
        if machine == 0x14C:
            return "x86"
        if machine == 0xAA64:
            return "arm64"
    except Exception:  # pefile is noisy on some system binaries
        return None
    return None