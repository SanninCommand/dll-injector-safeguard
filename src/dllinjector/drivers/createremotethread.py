"""Classic CreateRemoteThread + LoadLibraryW injection backend.

This is the most compatible backend and the one most likely to trip
anti-cheat / EDR heuristics. It writes the DLL path into the target's
address space, resolves LoadLibraryW, and spawns a thread that calls it.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

from dllinjector.models.job_model import Job
from dllinjector.services.telemetry import get_logger

log = get_logger(__name__)

PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT_RESERVE = 0x3000
PAGE_READWRITE = 0x04

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.VirtualAllocEx.restype = wintypes.LPVOID
kernel32.VirtualAllocEx.argtypes = [
    wintypes.HANDLE, wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD
]
kernel32.WriteProcessMemory.argtypes = [
    wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)
]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetProcAddress.restype = wintypes.LPVOID
kernel32.CreateRemoteThread.restype = wintypes.HANDLE


def inject(job: Job, timeout_ms: int = 5000) -> None:
    """Inject job.dll_path into job.pid. Raises OSError on failure."""
    h