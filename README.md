# My Glove80

QWERTY and Gaming, wireless use, and meaningful key colors over normal RGB
animations. This project uses Colonel's Glove80 firmware and Rynkbench editor.
**Both halves run RMK. USB/Bluetooth configuration and split lighting sync have
been verified; sleep/wake and battery endurance remain unqualified.**

## Start working

From this directory, enable the pinned environment once:

```sh
direnv allow
```

It loads automatically when you enter the directory. Without direnv, run
`nix develop`. Both provide `just`, the pinned Rust toolchain, and the editor’s
Node/Python dependencies. Type `just` to see the available commands.

## Change the layout

```sh
just edit
```

This opens unmodified Rynkbench. Choose **Open file** and select
`config/runtime.toml`. Edit keys and lighting visually, then **Download TOML**.
Adopt the downloaded file with:

```sh
just save ~/Downloads/NAME-rynkbench.toml
```

This validates the file and backs up the previous project configuration. Use the
actual downloaded filename. Rynkbench does not save directly into this repo.
You do not need to edit TOML text.

Once the keyboard runs RMK, you can instead connect it in Rynkbench over USB
or paired Bluetooth and edit live. Those changes affect the keyboard immediately. Close its device connection
and run `just pull` afterward to keep the repo current.

To put the saved layout on an already configured RMK keyboard, close any other
device configurator and run:

```sh
just apply
```

The `just` device recipes default to Bluetooth. Use `just apply --usb` to
require a cable. The underlying `./keyboard apply` still selects automatically
(USB preferred, otherwise BLE). The same options work with `pull`, `diff`, and
`backup`; see [transport selection](docs/firmware.md#transport-selection).

This checks the configuration, backs up the keyboard, checks for conflicting
live edits, writes it, and verifies readback. A failed check stops the operation.
If you edited the keyboard directly in another configurator, `just pull`
saves those edits into this project and backs up the previous project file.

For the **first installation**, follow [first install](docs/first-install.md).
The first apply requires `--replace-live`; the normal apply never silently
replaces device changes it has not seen before.

## Find things

- [Controls](docs/controls.md): Gaming toggle, Magic, wireless and lighting.
- [First install and recovery](docs/first-install.md): flashing and the hardware trial.
- [Evaluation](docs/evaluation.md): what was checked, changes from ZMK, and open risks.
- [Maintenance](docs/firmware.md): builds, dependencies, backups and updates.

`just status` shows local readiness; `just check` runs offline checks.
`just` lists commands. Commands require Linux, Git, and Nix with flakes;
the locked flake supplies the remaining tools. The first build needs
network access and several GB of free build space. Nothing here changes NixOS
configuration or flashes firmware automatically.
