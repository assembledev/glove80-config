# My Glove80

QWERTY and Gaming, wireless use, and meaningful key colors over normal RGB
animations. This project uses Colonel's Glove80 firmware and Rynkbench editor.
**Both halves run RMK. USB/Bluetooth configuration and split lighting sync have
been verified; sleep/wake and battery endurance remain unqualified.**

## Change the layout

From this directory:

```sh
./keyboard edit
```

This opens unmodified Rynkbench. Choose **Open file** and select
`config/runtime.toml`. Edit keys and lighting visually, then **Download TOML**.
Adopt the downloaded file with:

```sh
./keyboard save ~/Downloads/NAME-rynkbench.toml
```

This validates the file and backs up the previous project configuration. Use the
actual downloaded filename. Rynkbench does not save directly into this repo.
You do not need to edit TOML text.

Once the keyboard runs RMK, you can instead connect it in Rynkbench over USB
or paired Bluetooth and edit live. Those changes affect the keyboard immediately. Close its device connection
and run `./keyboard pull` afterward to keep the repo current.

To put the saved layout on an already configured RMK keyboard, close any other
device configurator and run:

```sh
./keyboard apply --ble
```

Omit `--ble` for automatic selection (USB preferred, otherwise BLE), or use
`--usb` to require a cable. The same options work with `pull`, `diff`, and
`backup`; see [transport selection](docs/firmware.md#transport-selection).

This checks the configuration, backs up the keyboard, checks for conflicting
live edits, writes it, and verifies readback. A failed check stops the operation.
If you edited the keyboard directly in another configurator, `./keyboard pull`
saves those edits into this project and backs up the previous project file.

For the **first installation**, follow [first install](docs/first-install.md).
The first apply requires `--replace-live`; the normal apply never silently
replaces device changes it has not seen before.

## Find things

- [Controls](docs/controls.md): Gaming toggle, Magic, wireless and lighting.
- [First install and recovery](docs/first-install.md): flashing and the hardware trial.
- [Evaluation](docs/evaluation.md): what was checked, changes from ZMK, and open risks.
- [Maintenance](docs/firmware.md): builds, dependencies, backups and updates.

`./keyboard status` shows local readiness; `./keyboard check` runs offline checks.
`./keyboard help` lists commands. Commands require Linux, Git, and Nix with flakes;
the pinned project shell supplies the remaining tools. The first build needs
network access and several GB of free build space. Nothing here changes NixOS
configuration or flashes firmware automatically.
