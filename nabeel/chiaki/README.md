# NABEEL Station — Chiaki Remote Play integration

This repository tracks upstream `streetpea/chiaki-ng` and keeps NABEEL-specific integration outside upstream source.

## Runtime contract

- PlayStation pairing credentials are local secrets and MUST NOT be committed.
- Prefer wired LAN between PlayStation and Ubuntu station.
- The integration launcher must fail closed when no Chiaki/chiaki-ng executable is installed.
- Controller, video, and audio remain local workstation concerns; no provider/business effects are involved.

## Acceptance sequence

1. Run `bash nabeel/chiaki/preflight.sh`.
2. Pair the PlayStation interactively using Chiaki's supported UI/CLI.
3. Verify a local gameplay + audio stream.
4. Disconnect/reconnect and verify readback.
5. Confirm `git status --short` contains no pairing credential material.

Physical pairing and gameplay acceptance cannot be certified from source CI alone.
