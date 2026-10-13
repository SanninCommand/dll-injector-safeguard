"""Load and validate the safety-check config from YAML."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from dllinjector.models.config_model import ConfigModel
from dllinjector.services.telemetry import get_logger

log = get_logger(__name__)


class ConfigError(RuntimeError):
    """Raised when the config file is missing, malformed, or fails validation."""


def load_config(path: Path) -> ConfigModel:
    """Read `path`, parse YAML, validate against ConfigModel, return it.

    Raises ConfigError on any failure — missing file, YAML syntax, or
    pydantic validation. Callers should treat this as fatal.
    """
    if not path.exists():
        raise ConfigError(f"config not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"config YAML parse failed: {exc}") from exc

    try:
        cfg = ConfigModel.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"config validation failed:\n{exc}") from exc

    _warn_on_disabled_checks(cfg)
    return cfg


def _warn_on_disabled_checks(cfg: ConfigModel) -> None:
    """Emit a startup warning for every processor the user turned off."""
    for name, section in cfg.processors.model_dump().items():
        if isinstance(section, dict) and section.get("enabled") is False:
            log.warning("processor disabled in config", extra={"processor": name})