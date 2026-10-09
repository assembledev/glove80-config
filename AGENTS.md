# AGENTS.md

## Project and ownership

Personal Glove80 layout on MoErgo's supported ZMK firmware.

- `config/glove80.keymap`: keys, layers, behaviors, macros and combos in MoErgo's
  physical 80-key order.
- `config/glove80.conf`: optional Kconfig overrides. Keep board, power, radio,
  flash and electrical settings at MoErgo defaults unless a diagnosed need
  justifies an explicit change.
- `config/default.nix`, `flake.nix`, `flake.lock`: official firmware source,
  native Nix builds and combined UF2 packaging.
- `scripts/zmk-keyboard`, `scripts/check-zmk.py`: active commands and source checks.
- `scripts/drop-firmware.py`, `tests/test_drop_firmware.py`: host-side firmware
  transfer and its checks; no custom code is added to the keyboard firmware.
- `backups/` and `artifacts/`: private recovery data and physical qualification
  evidence; retain Git exclusions.

## Changes and verification

Keep keys outside the requested change intact. Check physical position order,
layer indices and combo references when editing the layout.

The native keymap is the source of truth. Use built-in ZMK behaviors and MoErgo's
builder. Keep edits scoped to the request; explicitly discuss changes to timing,
behavior defaults or Kconfig before making them. Do not introduce JSON converters,
alternate editors, custom firmware patches or live-configuration tooling.

Run `./keyboard check` for source changes and `nix flake check` for Nix or command
changes. These do not compile firmware. Build with `./keyboard build-firmware`
only when firmware compilation is authorized. Compilation does not establish
physical behavior; follow [validation](docs/evaluation.md).

Do not commit, add remotes, publish, apply configuration or flash hardware unless
requested. Before flashing, verify the target volume, firmware packaging and
available recovery image using [installation](docs/first-install.md).

## Documentation

README owns the editing workflow; controls owns key behavior; firmware owns
source/build maintenance; first-install owns flashing/pairing/recovery; evaluation
owns verification boundaries. Document durable interfaces and operations, not
patch chronology or transient test results. Never include private data or secrets.
