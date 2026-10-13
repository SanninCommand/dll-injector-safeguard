# Security Policy

## Scope

`dll-injector-safeguard` is a **local, user-invoked** DLL injector with an
explicit safety-check pipeline. It is not a service, it does not listen on
any socket, and it never phones home. If you find a way to make it inject
without running the checks — that's a vulnerability and we want to hear it.

## Reporting a Vulnerability

Email `security@dll-injector-safeguard.dev` (PGP key in `docs/pgp.txt`).
Include:

- Version (`dllinjector --version`) and Windows build (`winver`).
- The exact `Job` YAML or CLI flags used.
- Whether the safety pipeline was bypassed, and how.
- A minimal repro — target process, DLL, and observed vs expected behavior.

We acknowledge within 72 hours. Fixes for pipeline-bypass issues ship in a
patch release within 14 days.

## Threat Model

In scope:
- Bypassing a processor by crafting a malformed `Job`.
- Path-allowlist escapes via symlinks, junction points, or 8.3 short names.
- Signature-check bypass via catalog spoofing or self-signed lookalikes.
- TOCTOU between the safety check and the actual `LoadLibrary` call.

Out of scope:
- Running the tool as an admin and expecting it to refuse admin actions.
- Injecting into Protected Process Light (PPL) targets — we refuse those
  by design and do not consider "it didn't work" a bug.
- Anti-cheat / EDR detection. This is a hobbyist injector, not a stealth
  loader. If you want evasion, fork it.

## Hardening Defaults

- `config/default.yaml` ships with `require_signature: true` and
  `require_arch_match: true`.
- The path allowlist is empty by default — you must opt in.
- `SeDebugPrivilege` is only requested when `--elevate` is passed.