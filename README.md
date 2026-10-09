# Glove80 configuration

Personal Base, Lower, Magic and Gaming layers for MoErgo's supported ZMK firmware.
The layout is in `config/glove80.keymap`; the firmware source and its development
tools are pinned through Nix.

## Build from a clone

Requires Linux and Nix with flakes enabled. Git submodules are not needed for the
ZMK workflow. On the computer that will flash the keyboard:

```sh
git clone https://github.com/assembledev/glove80-config.git
cd glove80-config
./keyboard check
./keyboard build-firmware
```

`check` preprocesses the keymap with the pinned ZMK headers and checks its device
tree, physical binding counts, behavior arguments and combo references. It does
not compile firmware. `build-firmware` builds both halves and produces
`result/glove80.uf2`, MoErgo's combined image. Flashing is manual: follow
[installation and recovery](docs/first-install.md).

## Edit the layout

Edit `config/glove80.keymap`, run `./keyboard check`, then rebuild and flash the
combined image. Use `nix develop` or `direnv allow` for a development shell;
`just check` and `just build-firmware` invoke the same commands.

- [Controls](docs/controls.md): layers, shortcuts, Bluetooth and RGB.
- [Firmware maintenance](docs/firmware.md): ownership, builds and source updates.
- [Installation and recovery](docs/first-install.md): flashing and pairing.
- [Validation](docs/evaluation.md): source checks and physical acceptance checks.

## License

[GNU GPLv3](LICENSE). Upstream firmware retains its own license.
