# Contributing to dll-injector-safeguard

Thanks for wanting to push the injector forward. This project is a Windows
desktop DLL injector with a mandatory safety-check pipeline bolted onto
every injection path. Contributions are welcome, but the guardrails are
not optional and PRs that bypass them get closed.

## Ground Rules

1. **Every injection goes through the pipeline.** No handler may call
   `LoadLibrary` / `CreateRemoteThread` / `NtCreateThreadEx` directly.
   Handlers emit a `Job`; processors validate it; the output driver is
   the only thing that touches the target process.
2. **Safety checks are additive, never subtractive.** If you add a new
   check, it runs. If you want to disable one, add a config flag and
   document the tradeoff in `docs/`.
3. **Tests ship with code.** A new processor without a unit test is a
   PR that won't merge.
4. **No silent privilege escalation.** Anything that touches `SeDebugPrivilege`
   must log at INFO before and after.

## Dev Setup

```powershell
git clone https://github.com/<you>/dll-injector-safeguard
cd dll-injector-safeguard
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
```

## Architecture in One Paragraph

`src/dllinjector/bootstrap` boots the CLI, loads config, and hands a
`Job` to `src/dllinjector/pipeline`. The pipeline runs ingest handlers
(`handlers/`) that normalize the request, then processors (`processors/`)
that run the safety checks in order — signature, path allowlist, target
integrity, arch match, privilege. If every check passes, the output
driver (`drivers/`) performs the actual injection using one of the
backends (CreateRemoteThread, QueueUserAPC, SetWindowsHookEx). Every
stage emits a structured event to `services/telemetry` so runs are
auditable after the fact.

## Coding Style

- Python 3.11+, `ruff` + `black`, line length 100.
- Type hints on every public function.
- No bare `except:` — catch `OSError`, `ctypes.WinError`, or `InjectorError`.
- Log through `services.telemetry.get_logger()`, never `print`.

## Commit Messages

`area: short imperative summary` — e.g. `processors: add PE arch mismatch check`.