"""Inspect the DLL to be injected and produce a DllFacts record."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pefile

from dllinjector.services.telemetry import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class DllFacts:
    path: Path
    sha256: str
    size_bytes: int
    machine: str | None
    is_dll: bool
    has_signature: bool
    signer: str | None


def inspect_dll(path: Path) -> DllFacts:
    """Parse PE headers, hash the file, and detect an Authenticode signature."""
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()

    machine = None
    is_dll = False
    try:
        pe = pefile.PE(data=data, fast_load=True)
        is_dll = bool(pe.FILE_HEADER.Characteristics & 0x2000)
        machine = {
            0x8664: "x64",
            0x14C: "x86",
            0xAA64: "arm64",
        }.get(pe.FILE_HEADER.Machine)
        pe.close()
    except pefile.PEFormatError:
        log.warning("dll is not a valid PE", extra={"path": str(path)})

    has_sig, signer = _check_signature(path)
    return DllFacts(
        path=path,
        sha256=digest,
        size_bytes=len(data),
        machine=machine,
        is_dll=is_dll,
        has_signature=has_sig,
        signer=signer,
    )


def _check_signature(path: Path) -> tuple[bool, str | None]:
    """Return (has_signature, signer_subject). Uses WinVerifyTrust on Windows."""
    try:
        from dllinjector.utils.win_trust import verify_authenticode

        return verify_authenticode(path)
    except ImportError:
        # Non-Windows dev box — report unknown rather than crashing.
        return False, None