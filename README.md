# Glove80 configuration

Personal Glove80 layout with QWERTY, Lower, Magic and Gaming layers, per-key
lighting, and Bluetooth configuration. Built on
[MoErgo RMK](https://github.com/colonelpanic8/moergo-rmk) and the
[Rynkbench](https://github.com/colonelpanic8/rynkbench) visual editor.

## Setup

Requires Linux, Git, and Nix with flakes enabled. From the repository root:

```sh
git submodule update --init --recursive
nix develop
```

For automatic environment loading, use `direnv allow` instead of `nix develop`.
Run `just` to list available commands. The first editor build needs network
access and several GB of free space.

Before applying a layout to a new keyboard, follow
[firmware installation and recovery](docs/first-install.md).

## Edit and apply

```sh
just edit
```

In Rynkbench, choose **Open file**, select `config/runtime.toml`, and edit the
layout. Choose **Download TOML** when finished, then import the downloaded file
and apply it to the keyboard:

```sh
just save ~/Downloads/NAME-rynkbench.toml
just apply
```

Replace `NAME-rynkbench.toml` with the downloaded filename. `save` updates the
project and keeps a backup; `apply` writes to the keyboard and verifies readback.
Device commands use Bluetooth by default and require a paired keyboard. Use
`just apply --usb` for USB; see [connection requirements](docs/firmware.md#transport-selection).

If you changed settings directly on the keyboard, run `just pull` before editing
to save them into the project. `just diff` compares the project with the keyboard.
Applying stops if there are unsynced device changes.

For direct editing through a browser device connection, see
[live editing and browser support](docs/firmware.md#commands).

## Documentation

- [Controls](docs/controls.md): layer shortcuts, workspace switching and RGB.
- [Installation and recovery](docs/first-install.md): flashing and restoring firmware.
- [Maintenance](docs/firmware.md): builds, dependencies, connections and backups.
- [Evaluation](docs/evaluation.md): validation results and hardware limitations.
