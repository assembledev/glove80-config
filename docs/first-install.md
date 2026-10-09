# Installation and recovery

## Prepare on the flashing computer

Have a USB data cable, a spare keyboard or on-screen keyboard, and a known-working
firmware image for recovery. Keep recovery images and saved layouts in a safe
location; this repository's ignored `backups/` and `artifacts/` are absent from a
fresh clone. A layout file alone is not a firmware recovery image.

From the clone, run:

```sh
./keyboard check
./keyboard build-firmware
```

The result is `result/glove80.uf2`, one combined image for both halves. Keep a copy
of the file with the source commit before flashing. The saved keymap is compiled
into this image; there is no separate live-configuration apply step.

## Flash both halves

Start the autodropper while you can still type:

```sh
./keyboard drop-firmware
```

It checks the current `result/glove80.uf2`, saves a copy under `artifacts/`, and
waits for mounted USB bootloader volumes. Your desktop must mount the volumes
automatically (or mount them before starting). It checks the volume label and
`INFO_UF2.TXT` board identity, backs up that half's `CURRENT.UF2`, then copies the
combined image. It waits for the bootloader volume to disappear before recording
completion, processes each half once, and exits after both. Either half may be
connected first. No dragging files or typing between halves is needed.

Use `./keyboard drop-firmware --dry-run` to check the image and currently mounted
volumes without writing. An optional UF2 path selects a different combined image:
`./keyboard drop-firmware path/to/glove80.uf2`. Ctrl+C stops waiting. A copy error
stops the command; inspect the reported recovery directory before retrying.
The command does not compile firmware, reset settings or change pairings.

Follow MoErgo's [firmware loading procedure](https://docs.moergo.com/glove80-user-guide/customizing-key-layout/#loading-new-zmk-firmware-onto-your-glove80).
Use the power-up bootloader method, which works independently of the installed
layout:

1. Switch the half off and connect it to the computer by USB.
2. Hold physical positions **C6R6 + C3R3** and switch it on. On default keycaps,
   these are **Magic + E** on the left and **I + PgDn** on the right.
3. Verify the mounted volume: `GLV80LHBOOT` is left; `GLV80RHBOOT` is right.
4. Let the autodropper copy the firmware and report that the volume disappeared.
   Alternatively, manually copy **the same `result/glove80.uf2`** to the volume.
5. Repeat for the other half.

When changing firmware families or versions, follow MoErgo's
[configuration reset and split-pairing procedure](https://docs.moergo.com/glove80-user-guide/troubleshooting/#configuration-factory-reset-and-re-pairing-left-and-right-halves).
This clears saved configuration and bonds; have both halves available and expect
to pair the host devices again. It does not replace the compiled personal layout.

## Check USB and pair Bluetooth

Return to Base and press Magic+left GUI to select USB output. Verify typing from
both halves, workspace holds and the Gaming toggle.

Select a [Bluetooth profile](controls.md#magic), remove the old keyboard pairing
from the intended host if necessary, and pair Glove80 in the host's Bluetooth
settings. Profile selection also prefers Bluetooth output. Disconnect USB and
verify both halves again. Clear only the selected profile when repairing one
host's pairing.

Complete the [physical acceptance checks](evaluation.md#physical-checks) before
relying on the setup.

## Recovery

Enter the hardware bootloader using the power-up method above and load the saved
working image according to its own packaging instructions. A MoErgo combined
image goes to both halves; separate images must match the target half. Restore
pairings as required by that firmware.

To recover from a bad keymap while keeping ZMK, restore a known-working
`config/glove80.keymap` from Git, build again and flash the combined image.
