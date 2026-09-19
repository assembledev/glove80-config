# Installation and recovery

This guide installs the firmware built by this repository on both Glove80
halves, then loads the saved layout. For routine layout changes, use the
[editing workflow](../README.md#edit-and-apply).

## Prepare

Complete the [environment setup](../README.md#setup). Have a USB data cable,
a spare keyboard or on-screen keyboard, and a known-working firmware image
for recovery. Keep the recovery image in `backups/rollback/` or another safe
location. A layout JSON alone cannot restore firmware.

Build a matching image pair from the checked-out configuration:

```sh
just build-firmware
just check
```

A fresh clone contains no firmware images. A successful build creates a dated
bundle and points `artifacts/current` to it. The bundle's `manifest.json`
identifies the left and right UF2 files; retain the bundle with its checksums
and configuration snapshots. Always use both halves from the same build.

## Flash both halves

Use MoErgo's [power-up bootloader procedure](https://docs.moergo.com/glove80-user-guide/customizing-key-layout/#entering-bootloader-mass-storage-device-mode-on-power-up):

1. Switch the half off and connect it to the computer by USB.
2. Hold physical positions **C6R6 + C3R3** and switch it on. On default keycaps,
   these are **Magic + E** on the left and **I + PgDn** on the right.
3. Check the mounted volume: `GLV80LHBOOT` is left; `GLV80RHBOOT` is right.
4. Copy the matching UF2 from the build bundle to that volume. Wait for the copy
   to finish and the volume to disappear.
5. Repeat for the other half.

## Load the layout

Turn on both halves and connect the left half by USB. Ensure the user has
[USB configuration access](firmware.md#transport-selection), then run:

```sh
just control --usb version
just diff --usb
just apply --usb --replace-live
```

Review the differences before applying. The first apply needs `--replace-live`
because this checkout has no saved synchronization baseline. It backs up the
keyboard configuration before replacing it. `diff` returns a nonzero status for
both differences and connection errors; resolve connection errors before applying.

Flashing and applying are separate operations: a fresh installation can use the
upstream default layout until the runtime configuration is applied. Removing a
layer from a file does not erase an existing device layer; see
[layer removal](firmware.md#layer-removal) if extra default layers remain.

## Pair Bluetooth

With the saved layout loaded, return to Base and select a Bluetooth slot using
[Magic](controls.md#magic). Pair the keyboard in the host's Bluetooth settings,
then disconnect USB and check typing from both halves. Switching firmware can
require removing the old host pairing and pairing again. Clear only the selected
slot's bond when repairing that slot; clearing all bonds affects every host.

Once paired, `just diff` checks the Bluetooth configuration connection. Complete
the [hardware checks](evaluation.md#hardware-checks) before relying on the setup.

## Recover

To restore a saved layout while keeping RMK, inspect the chosen backup, then run:

```sh
just save backups/CHOSEN.toml
just apply --replace-live
```

Use the actual backup filename and add `--usb` to `apply` when using USB.
Both operations retain a backup of what they replace.

To restore firmware, enter each half's hardware bootloader using the power-up
procedure above and flash the known-working recovery image according to its
instructions. Recovery images may use a different packaging scheme from this
project's separate left/right UF2s. Restore host pairings as required by that
firmware. A settings reset does not reinstall firmware.
