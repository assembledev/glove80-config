# Firmware maintenance

## Ownership

| Path | Purpose |
|---|---|
| `config/glove80.keymap` | Physical keys, layers, hold/taps, macros and combos |
| `config/glove80.conf` | Optional Kconfig overrides; currently uses MoErgo defaults |
| `config/default.nix` | MoErgo's left/right builds and combined UF2 packaging |
| `flake.nix`, `flake.lock` | Pinned official ZMK source and Linux development environment |
| `scripts/zmk-keyboard`, `scripts/check-zmk.py` | Command entry point and source validation |
| `scripts/drop-firmware.py` | Validated UF2 transfer to mounted bootloader volumes |

The build uses the Nix builder shipped by `moergo-sc/zmk` and that revision's
pinned nixpkgs. Board wiring, flash layout, radio policy, power management and
RGB limits belong to MoErgo's firmware. Do not duplicate them in this repository
without a diagnosed, explicit need.

A normal clone is sufficient; the build requires no Git submodules. Private
layouts and recovery data live in Git-ignored `backups/` and `artifacts/`; they are
not supplied by cloning the repository.

## Commands

```sh
./keyboard check
./keyboard build-firmware
./keyboard drop-firmware
```

The commands use the live checkout. The build writes the `result` link to a Nix
store directory containing `glove80.uf2`. This single combined image contains
both board-specific families and is copied to both halves. Checking and building
do not flash hardware. `drop-firmware` explicitly transfers an existing image;
see [installation](first-install.md). These commands do not change pairing.

`nix develop` supplies the command tools, MoErgo's firmware build dependencies,
and the pinned Zephyr modules and source. Entering the shell fetches or builds
those dependencies without compiling firmware. Dependencies are shared with
the firmware builder rather than maintained as a separate toolchain list.
Changing the firmware pin or garbage-collecting dependencies can require new
downloads. See
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
