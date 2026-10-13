"""Pydantic models mirroring config/default.yaml."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class PipelineSection(BaseModel):
    fail_fast: bool = True
    emit_telemetry: bool = True
    max_job_age_seconds: int = 30


class TargetAliveSection(BaseModel):
    enabled: bool = True
    refresh_snapshot_ms: int = 250


class ArchMatchSection(BaseModel):
    enabled: bool = True
    allow_wow64_bridge: bool = False


class DllSignatureSection(BaseModel):
    enabled: bool = True
    require_signed: bool = True
    trusted_publishers: list[str] = Field(default_factory=list)
    allow_catalog_signed: bool = True


class PathAllowlistSection(BaseModel):
    enabled: bool = True
    allowed_roots: list[Path] = Field(default_factory=list)
    resolve_symlinks: bool = True
    reject_unc: bool = True


class PrivilegeCheckSection(BaseModel):
    enabled: bool = True
    require_se_debug: bool = True
    auto_elevate: bool = False


class ProtectedProcessGuardSection(BaseModel):
    enabled: bool = True
    deny_system_processes: bool = True
    denied_names: list[str] = Field(default_factory=list)


class ProcessorsSection(BaseModel):
    target_alive: TargetAliveSection = TargetAliveSection()
    arch_match: ArchMatchSection = ArchMatchSection()
    dll_signature: DllSignatureSection = DllSignatureSection()
    path_allowlist: PathAllowlistSection = PathAllowlistSection()
    privilege_check: PrivilegeCheckSection = PrivilegeCheckSection()
    protected_process_guard: ProtectedProcessGuardSection = ProtectedProcessGuardSection()


class BackendSection(BaseModel):
    wait_for_load: bool = True
    require_alertable_thread: bool = True
    hook_scope: str = "thread"
    timeout_ms: int = 5000


class DriversSection(BaseModel):
    default_backend: str = "createremotethread"
    backends: dict[str, BackendSection] = Field(default_factory=dict)


class TelemetrySection(BaseModel):
    log_dir: Path = Path("logs")
    level: str = "INFO"
    json_events: bool = True
    redact_paths: bool = False


class ConfigModel(BaseModel):
    pipeline: PipelineSection = PipelineSection()
    processors: ProcessorsSection = ProcessorsSection()
    drivers: DriversSection = DriversSection()
    telemetry: TelemetrySection = TelemetrySection()