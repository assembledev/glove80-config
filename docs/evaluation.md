# Validation

## Source checks

`./keyboard check` and the flake's `keymap` check preprocess the saved layout
using the pinned official ZMK headers, compile its device tree, and check:

- Every layer has 80 bindings in the official board's physical position order.
- Referenced behaviors exist and have the required number of arguments.
- Hold/tap targets, layer references and combo positions are valid.
- The command scripts and `just` recipes have valid syntax.

This does not compile firmware or validate the complete board device tree and
Kconfig. A successful firmware build additionally verifies the Zephyr build and
produces the combined UF2. Neither establishes physical keyboard reliability.

## Physical checks

After installing a build, verify:

| Area | Procedure |
|---|---|
| Keys | Exercise every physical key on all four layers, including thumb keys |
| Holds | Tap F1–F5; hold each and keep holding; check one workspace switch and no held Super |
| Gaming | Enter with Base B + Right Arrow and leave with Gaming F + C |
| USB | Select USB output and exercise overlapping presses/releases on both halves |
| Bluetooth | Repeat typing on each intended host; look for missing releases and unintended repeat |
| Wake | Test the first key after idle, host suspend and keyboard power cycles, from each half |
| RGB | Verify toggle, brightness, effects and Magic's status indicators on both halves |
| Persistence | Power-cycle both halves and verify layout, output selection and lighting state |
| Endurance | Charge each half fully and record normal-use intervals with RGB off |

Keep private observations, source revisions and firmware copies under ignored
`artifacts/`. Distinguish actual shutdown from displayed battery percentage.
Battery estimates alone do not measure endurance. A comparison is meaningful
only with the same hosts, lighting policy and comparable starting charge.
