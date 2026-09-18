# Maintenance

## What we use from Colonel

| Component | Owner | Our use |
|---|---|---|
| Glove80 hardware, builds, host CLI | `dependencies/moergo-rmk` | Pinned submodule; owns its nested RMK, PaletteFX and assembly revisions |
| Visual keymap/lighting editor | `dependencies/rynkbench` | Pinned submodule; unmodified upstream editor |
| Personal config examples | Colonel's `moergo-config` | Reference only; not a dependency or the owner of our layout |
| Bindings and lighting | `config/runtime.toml` | Saved by the visual editor; applied through the host CLI |
| Board settings | `config/firmware.toml` | Compiled settings, including the five-minute sleep timeout |

The editor's WASM codecs are built from **our pinned firmware and RMK sources**,
not fetched from the changing hosted editor. `config/rynk-wasm-Cargo.lock` locks
its browser-side dependencies. There are no downstream source patches or injected editor features.

## Commands

| Command | Purpose |
|---|---|
| `./keyboard init` | Initialize pinned submodules after checkout |
| `./keyboard edit` | Serve upstream Rynkbench on a random localhost port; build it if missing |
| `./keyboard save FILE` | Validate a downloaded TOML and adopt it, with a backup |
| `./keyboard pull` | Export the selected keyboard into the project, preserving layer names |
| `./keyboard diff` | Show project/device differences; nonzero can mean differences or a connection error |
| `./keyboard backup` | Save a private live export without changing the project |
| `./keyboard apply` | Back up, reject unsynced device edits, preview, write, verify and record sync |
| `./keyboard apply --replace-live` | Explicitly replace an unsynced device configuration, still with backup and verification |
| `./keyboard check` | Validate runtime, run transaction/server regressions, check pins and current images |
| `./keyboard build-editor` | Rebuild codecs and editor; run typechecking and its complete test suite |
| `./keyboard build-firmware` | Build both halves into a new timestamped bundle, with configuration snapshots and checksums |
| `./keyboard control ARGS` | Advanced upstream CLI access; can bypass project safeguards |

Only the apply/control commands can write to the keyboard. For offline editing, open the project TOML and download the edited TOML before
closing the browser; adopt it with `save`. For live editing, use Rynkbench’s USB or Bluetooth transport, then close its
device connection and run `pull` with the matching transport. The local server serves editor assets only and has no
project write API.
Use one device client at a time. There is no automatic background sync.

## Transport selection

`apply`, `pull`, `backup`, and `diff` share these options:

- No transport flag: upstream auto-selection prefers accessible USB, then BLE.
- `--ble`: require Bluetooth. Pair/bond the keyboard with the host first.
- `--usb`: require USB. This and `--ble` are mutually exclusive.
- `--device VALUE`: select a full BLE address or USB `/dev/hidraw*` path.
  An explicit selection must match; it does not select another keyboard on failure.

For example, `./keyboard pull --ble` saves wireless live edits, and
`./keyboard apply --ble --device AA:BB:CC:DD:EE:FF` targets a particular paired
keyboard (replace the example address). The selection is passed to every device
read, preview, write, and verification in that operation. Local file validation
remains offline. A failed explicit BLE operation is not retried over USB.

On Linux, USB configuration requires read/write access to the keyboard’s
Rynk `/dev/hidraw*` interface (USB interface 02, VID 16c0, PID 27db). A
bootloader drive being writable does not grant HID access. Device-node ACLs
are temporary and disappear on reconnect; a narrowly scoped host udev rule
is needed for persistent user access. This project does not install that rule.

Rynkbench supports Web Bluetooth as well as USB; browser support depends on the
platform. On Linux, Chromium may require its experimental web-platform flag;
see [Chrome's Web Bluetooth documentation](https://developer.chrome.com/docs/capabilities/bluetooth).
The native CLI BLE transport does not depend on browser Bluetooth support.
No wireless hardware qualification is implied by wrapper tests.

## Files and reproducibility

`backups/` contains original imports, replaced project files, live exports and
rollback images. `backups/last-synced.toml` is the last verified device snapshot;
it detects edits made outside the project. Losing it is safe: the next apply
requires an explicit replacement. `artifacts/` contains image bundles and
hardware results. Both directories are private and ignored by Git; copy them
into your normal backup system before moving to another machine.

`.cache/` is disposable tool/build output. Rebuilding the editor recreates it.
For a small build disk, set `GLOVE80_BUILD_CACHE` to an absolute directory on a
larger filesystem. RAM build directories disappear at reboot. The completed
editor's `dist/` is kept on disk, so ordinary editing does not need Rust builds.

`artifacts/current` points to the last successfully built bundle. An all-zero
configuration commit in its manifest means this project has no commit yet; the
saved files and `CONFIG_SHA256SUMS` identify its exact contents.

Firmware bundles contain separate LH/RH UF2s, a manifest, checksums, configuration
snapshots and a log. Do not mix halves from different bundles. Initial-trial
ELFs are compressed: its `ARTIFACTS.sha256` covers the delivered files, while
`SHA256SUMS` names the original uncompressed ELFs.

To update, inspect upstream changes, change the parent submodule pins
intentionally, update the expected pins in `scripts/evaluate.py`, then rebuild
both firmware and editor and repeat the hardware trial. Do not advance the
nested RMK fork independently. Retain the previous working image pair and live
config until the new pair passes. These tools do not create commits or remotes.
