# Maintenance

## Configuration and dependencies

| Path | Purpose |
|---|---|
| `config/runtime.toml` | Saved layers, bindings, behaviors and lighting; applied without reflashing |
| `config/firmware.toml` | Compiled board, power and hardware settings |
| `dependencies/moergo-rmk` | Pinned firmware and host CLI, including its nested RMK and lighting dependencies |
| `dependencies/rynkbench` | Pinned visual editor |
| `flake.lock` | Development environment and toolchain dependencies |
| `config/rynk-wasm-Cargo.lock` | Editor protocol codec dependencies |

The editor's WASM codecs are built from the pinned firmware and RMK sources.
Keep the firmware flake input and Git submodule on the same revision. Dependency
source trees remain unmodified.

## Commands

Use the [project environment](../README.md#setup), then run `just` for the full
command list. `./keyboard COMMAND` also works outside the environment and enters
it automatically.

| Command | Purpose |
|---|---|
| `just init` | Initialize pinned submodules |
| `just edit` | Build if needed and serve the editor on localhost |
| `just save FILE` | Validate and import an editor export, backing up the project file |
| `just pull` | Save live keyboard settings into the project |
| `just diff` | Compare the project with the keyboard |
| `just backup` | Export the keyboard into a private backup without changing the project |
| `just apply` | Back up, check for conflicts, preview, apply and verify readback |
| `just build-tools` | Rebuild the host CLI |
| `just build-editor` | Build and test the editor and codecs |
| `just build-firmware` | Build a matching left/right image bundle; flashing is manual |
| `just check` | Run the [offline checks](evaluation.md#automated-checks) |
| `just control ARGS` | Access the upstream CLI directly, bypassing project transaction safeguards |

Close other device configurators before a device operation. There is no
background synchronization. If apply reports unsynced device edits, use
`just pull` to retain them. Use `just apply --replace-live` only after reviewing
and choosing to replace the device configuration; it still takes a backup.

### Layer removal

Omitting a layer from TOML does not erase its device slot. Upstream
`config apply --exact` replaces omitted behavior tables but not omitted keymap
layers. Delete the layer through a live Rynkbench connection, which clears its
keymap and occupied/name metadata, then run `just pull`. An empty trailing slot
is omitted from exports; firmware layer capacity remains available.

## Transport selection

`just apply`, `pull`, `diff` and `backup` default to Bluetooth. They accept:

| Option | Behavior |
|---|---|
| `--ble` | Require Bluetooth; pair the keyboard with the host first |
| `--usb` | Require USB; cannot be combined with `--ble` |
| `--device VALUE` | Select a full BLE address or USB `/dev/hidraw*` path |

When supplying a device selector through `just`, include the intended transport,
for example `just diff --ble --device AA:BB:CC:DD:EE:FF` with the actual address.
The underlying `./keyboard` commands without transport flags prefer accessible
USB, then Bluetooth. An explicit transport or device failure does not trigger a
fallback to another device.

On Linux, USB configuration needs read/write access to the keyboard's Rynk
`/dev/hidraw*` interface: USB interface 02, VID `16c0`, PID `27db`. Bootloader
mass-storage access is separate. A temporary device-node ACL is lost on reconnect;
configure a narrowly scoped host udev rule for persistent access. This repository
does not install host rules.

### Live editing

`just edit` launches the browser version of Rynkbench. Opening and downloading a
layout file does not require browser access to the keyboard. Direct device
editing requires a transport supported by the browser:

- USB uses WebHID, or Web Serial where supported by the firmware.
- Bluetooth uses Web Bluetooth. Linux Chromium may need the experimental
  web-platform flag; consult [Chrome's documentation](https://developer.chrome.com/docs/capabilities/bluetooth).
- The editor's native USB and Bluetooth choices require the upstream desktop
  application, which `just edit` does not launch.

The editor disables a transport when its API is unavailable. The CLI's Bluetooth
connection is independent of browser support, so the file workflow remains usable
in browsers without device APIs. After live edits, close the editor's device
connection and run `just pull` to capture them.

## Builds and local data

Firmware builds create dated bundles under `artifacts/`; `artifacts/current`
points to the last successful bundle. Each contains separate left/right UF2s,
source/build metadata, checksums, configuration snapshots and a build log. Use
the manifest to identify images and keep each pair together.

`backups/` stores replaced project files and live device exports.
`backups/last-synced.toml` records the verified device state used for conflict
checks. Without it, apply requires an explicit replacement decision. Include
backups and recovery images in your own backup system: `backups/` and `artifacts/`
are ignored by Git and absent from a fresh clone.

`.cache/` contains disposable host tools and editor build output. To place editor
compiler output on another filesystem, set `GLOVE80_BUILD_CACHE` to an absolute
directory before running `just build-editor`. RAM-backed build directories are
lost on reboot. The completed editor remains in `.cache/editor/dist/`.

Nix uses Git-tracked project files. Add new flake-referenced files to Git before
checking them. Run `just fmt` after changing the flake.

## Dependency updates

1. Review upstream firmware and editor changes together for protocol and codec
   compatibility.
2. Update the parent submodule revisions. Initialize their nested dependencies
   with `git submodule update --init --recursive`; retain the nested revisions
   selected by the firmware project.
3. Match `inputs.firmware.url` in `flake.nix` to the firmware submodule and update
   its lock entry. Update `PINS` in `scripts/evaluate.py`. Review whether the
   editor codec's Cargo lock also needs updating.
4. Run the [automated checks](evaluation.md#automated-checks), including fresh
   editor and firmware builds.
5. Back up the live configuration, keep the previous working image pair, install
   the new pair, and perform the [hardware checks](evaluation.md#hardware-checks).

Retain the previous bundle and recovery image until the new installation has
passed the checks you rely on.
