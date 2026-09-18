# First install and recovery

Do this with a spare keyboard available. The firmware images have passed build
and image checks; BLE reliability, physical key behavior and battery use have
not yet been tested on this keyboard.

## Before flashing

Keep a **known-working ZMK UF2** in `backups/rollback/`. None is present yet.
The original JSON in `backups/original/source-layout.json` preserves your layout,
but cannot restore firmware by itself. Obtain the UF2 from your existing working
build or build that JSON with its required MoErgo firmware selection. Do not
mistake a bootloader's `CURRENT.UF2` dump for a verified recovery image.

Run `./keyboard check`. The checked RMK pair is in
`artifacts/current/`: `glove80-rmk-0.1.0-lh.uf2` and
`glove80-rmk-0.1.0-rh.uf2`. Keep the pair together. If compiled settings or
firmware revisions change, run `./keyboard build-firmware` and use the newly
created bundle instead.

## Install and load your layout

1. Use MoErgo's [hardware bootloader procedure](https://docs.moergo.com/glove80-user-guide/customizing-key-layout/#putting-glove80-into-bootloader-for-firmware-loading):
   switch a half off, connect USB, hold physical C6R6+C3R3, and switch on.
   On the original layout these are Magic+E on the left, I+PgDn on the right.
2. Check the volume name. Copy **LH only to GLV80LHBOOT**, and **RH only to
   GLV80RHBOOT**. These RMK images are separate, unlike a combined ZMK image.
   Wait for each copy to finish and its bootloader volume to disappear.
3. Turn on both halves and connect the left half by USB. Run
   `./keyboard control --usb version`. A new flash initially uses the upstream
   layout until you apply yours.
4. Run `./keyboard diff` to inspect the initial differences, then
   `./keyboard apply --replace-live`. This saves the initial live configuration
   before writing yours. A command failure is a stop, not a reason to flash again.
5. Check USB typing from both halves, then follow the trial below. Changing from
   ZMK to RMK can require removing the old host Bluetooth pairing and pairing anew.

## Hardware trial

Record results in `artifacts/hardware-trial.md`, including the firmware bundle
and date. Keep the rollback image until all of these pass:

| Check | Pass condition |
|---|---|
| QWERTY | Every key on both halves produces its expected output; eight tap/holds behave acceptably during actual typing |
| Gaming | All Gaming keys work; B+Right / F+C enters and exits repeatedly, with no stuck keys |
| Wireless | Pair a Magic thumb slot; type on both halves with USB unplugged; reconnect after power cycling |
| Sleep | After more than five idle minutes, LEDs go out and a key on **either** half wakes typing and the split link |
| Persistence | Power-cycle both halves; bindings, scenes, selected effect and output policy survive |
| Lighting | Eight Lower highlights remain visible over a changing effect; disappear when Lower ends; Magic indicators match state |
| Battery | Compare a normal evening and overnight idle with lights off, then with your preferred lights; record both halves' starting/ending percentages and elapsed time |

The intended target is comfortable wireless use with charging available, not a
month of battery life. If wake loses the first key, the right half disconnects,
or Gaming becomes unreliable, stop the trial and restore ZMK. If only LED drain
is excessive, try Magic+S (no animation), then Magic+T (lights off), before
changing radio timing. Battery percentages are coarse; do not extrapolate a
short test into a lifetime estimate.

## Recover

Enter each half's hardware bootloader using the physical power-up method above,
then restore your known-working ZMK image to the appropriate half (or both if
it is a combined MoErgo image). Follow MoErgo's reset/re-pair instructions if
Bluetooth bonds no longer match. Resetting RMK does not reinstall ZMK.

To recover a layout while staying on RMK, use
`./keyboard save backups/CHOSEN.toml`, then `./keyboard apply --replace-live`.
Both operations keep backups of what they replace.
