"""Command-line entry point for dll-injector-safeguard.

Builds a Job from CLI flags, loads config, and hands the job to the
pipeline. This module is the ONLY place user input becomes a Job.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from dllinjector import __version__
from dllinjector.bootstrap.config_loader import load_config
from dllinjector.bootstrap.job_builder import build_job
from dllinjector.pipeline.runner import PipelineRunner
from dllinjector.services.telemetry import configure_logging, get_logger

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()
log = get_logger(__name__)


@app.command()
def inject(
    process: str = typer.Option(..., "--process", "-p", help="Target process name or PID."),
    dll: Path = typer.Option(..., "--dll", "-d", help="Absolute path to the DLL to inject."),
    backend: str = typer.Option(
        "createremotethread",
        "--backend",
        "-b",
        help="Injection backend: createremotethread | queueuserapc | sethooksex.",
    ),
    config: Path = typer.Option(
        Path("config/default.yaml"), "--config", "-c", help="Path to safety-check config."
    ),
    elevate: bool = typer.Option(False, "--elevate", help="Request SeDebugPrivilege before inject."),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Run all safety checks, stop before the driver."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip the interactive confirm prompt."),
) -> None:
    """Inject a DLL into a target process after running the safety pipeline."""
    cfg = load_config(config)
    configure_logging(cfg.telemetry)

    job = build_job(
        process_spec=process,
        dll_path=dll,
        backend=backend,
        elevate=elevate,
        dry_run=dry_run,
        config=cfg,
    )

    if not yes and not dry_run:
        console.print(f"[bold]About to inject[/bold] {job.dll_path} -> PID {job.pid}")
        typer.confirm("Proceed?", abort=True)

    runner = PipelineRunner(cfg)
    result = runner.run(job)

    if result.ok:
        console.print(f"[green]injected[/green] {job.dll_path.name} into pid {job.pid}")
        sys.exit(0)
    console.print(f"[red]blocked[/red] at {result.failed_stage}: {result.reason}")
    sys.exit(2)


@app.command()
def version() -> None:
    """Print the tool version."""
    console.print(f"dll-injector-safeguard {__version__}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()