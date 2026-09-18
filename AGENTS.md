# AGENTS.md

## Project

Personal Glove80 configuration, firmware builds, and configuration tools using
MoErgo RMK and Rynkbench. Maintain reliable typing, wireless operation, and visual
layout editing through the supported upstream interfaces.

## Ownership

- `config/runtime.toml`: bindings, layers, behaviors, and lighting; applied at runtime.
- `config/firmware.toml`: board and power settings compiled into both halves.
- `scripts/`: project commands, configuration transactions, and build orchestration.
- `tests/`: project regressions and the personal-layout editor round trip.
- `dependencies/`: pinned upstream Git submodules. Keep their sources unmodified;
  use configuration and public interfaces rather than downstream patches.
- `.cache/`: disposable build output. `backups/` and `artifacts/`: private local
  recovery data and build/qualification evidence; retain their Git exclusions.

## Changes

- Keep bindings and controls outside the requested change intact. Layer reordering
  also requires checking layer references, combos, and lighting conditions.
- Preserve board wiring, flash partitions, and electrical limits when changing
  firmware settings.
- Preserve transaction guarantees: validate before replacement, retain the previous
  configuration, stop writes on failed device checks, and verify device readback.
- Update dependency pins as a compatible firmware/editor set using the procedure
  in [maintenance](docs/firmware.md). Keep nested firmware dependencies at the
  revisions selected by their parent.
- Do not commit, add remotes, or publish private files unless requested.

## Verification

Run commands from the repository root. Linux, Git, and Nix with flakes are
required. Use direnv or `nix develop`, then `just` recipes; `./keyboard`
also enters the pinned flake environment when invoked outside the shell. Use `./keyboard init`
when submodules are missing and `./keyboard help` for the command interface.

| Change | Required verification |
|---|---|
| Flake or task recipes | `nix flake check`, `nix develop --command just check` |
| Runtime configuration | `./keyboard validate` |
| Project scripts or tests | `./keyboard check` |
| Editor build, codec compatibility, or editor round-trip tests | `./keyboard build-editor` |
| Compiled settings or firmware dependency | `./keyboard check` and `./keyboard build-firmware` |
| Documentation only | Check referenced paths, commands, and `git diff --check` |

For dependency updates, combine the applicable checks. Add regression coverage
for changed behavior, especially configuration loss and failed device operations.
Report which checks ran and any remaining unverified behavior. Compilation and
host tests do not establish physical keyboard behavior; hardware qualification
follows [first install](docs/first-install.md).

## Device operations and documentation

- Apply configuration or flash firmware only when the task authorizes that device
  operation. Before flashing, verify the target half, matching image, and available
  recovery firmware using [first install](docs/first-install.md).
- Update the document that owns a changed interface: [README](README.md) for the
  editing workflow, [controls](docs/controls.md) for key behavior, and
  [maintenance](docs/firmware.md) for builds and dependency updates.
- Keep qualification findings in [evaluation](docs/evaluation.md), with supporting
  local evidence in `artifacts/`. Distinguish observed failures from untested behavior.
