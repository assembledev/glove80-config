# Firmware maintenance

## Ownership

| Path | Purpose |
|---|---|
| `config/glove80.keymap` | Physical keys, layers, hold/taps, macros and combos |
| `config/glove80.conf` | Optional Kconfig overrides; currently uses MoErgo defaults |
| `config/default.nix` | MoErgo's left/right builds and combined UF2 packaging |
| `flake.nix`, `flake.lock` | Pinned official ZMK source and Linux development environment |
| `scripts/zmk-keyboard`, `scripts/check-zmk.py` | Command entry point and source validation |

The build uses the Nix builder shipped by `moergo-sc/zmk` and that revision's
pinned nixpkgs. Board wiring, flash layout, radio policy, power management and
RGB limits belong to MoErgo's firmware. Do not duplicate them in this repository
without a diagnosed, explicit need.

The RMK TOML files, tooling, tests and upstream submodules are retained as frozen
reference and recovery source material. They are not used by the ZMK commands
or Nix outputs. A normal clone is sufficient; do not initialize submodules for
this workflow. Private layouts and recovery data live in Git-ignored `backups/`
and `artifacts/`; they are not supplied by cloning the repository.

## Commands

```sh
./keyboard check
./keyboard build-firmware
```

The commands use the live checkout. The build writes the `result` link to a Nix
store directory containing `glove80.uf2`. This single combined image contains
both board-specific families and is copied to both halves. Neither command
flashes hardware, changes pairing or applies live configuration.

Use `nix develop` for `just` and the source-check tools. See
[validation](evaluation.md) for the boundaries of these checks and
[installation](first-install.md) for the physical procedure.

## Update the firmware source

1. Review stable releases in [MoErgo ZMK](https://github.com/moergo-sc/zmk/releases).
2. Set `inputs.zmk.url` to the chosen release's full commit in `flake.nix` and run
   `nix flake lock` to record its content hash.
3. Run `./keyboard check` and `nix flake check`.
4. Build on the flashing computer, keep the current working recovery image,
   flash both halves and perform the physical checks in [validation](evaluation.md).

Firmware source updates can require clearing settings and pairing again. Keep
working firmware images independently of the Nix store and its garbage collection.
