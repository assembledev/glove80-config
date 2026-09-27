# Controls

Positions refer to the keys on Base. All four layers and their complete bindings
are defined in `config/glove80.keymap` in MoErgo's physical key order.

## Layers

| Layer | Access and purpose |
|---|---|
| Base | QWERTY typing and function keys |
| Lower | Hold Lower; navigation, keypad, media and display brightness |
| Magic | Hold Magic; Bluetooth, RGB and firmware controls |
| Gaming | Press Base B + Right Arrow together; dedicated gaming bindings |

The Gaming toggle has a 50 ms combo window. The same physical keys are F + C on
Gaming and toggle back to Base. Return to Base before using Magic.

A quick tap of Magic shows MoErgo's battery, connection and layer indicators.
Holding it enters Magic using MoErgo's usual 200 ms tap-preferred behavior.

## Right thumb keys

On Base and Lower, the physical right Alt position sends **Backspace**, and the
physical Backspace position sends **Right Alt**. Gaming is unchanged.

## Tap and hold

| Base key | Tap | Hold |
|---|---|---|
| F1–F5 | Corresponding function key | Send Super+F1–F5 once, then release Super |
| Print Screen | Print Screen | Super+Print Screen |
| 1 | 1 | Shift+1 |
| 7 | 7 | Shift+Slash |

These use ZMK's usual 200 ms hold threshold; function holds and the remaining
hold/taps use the default hold-preferred flavor. Workspace holds execute a
complete press/tap/release macro, so keeping the key held does not repeat the
shortcut or keep Super pressed. The host must bind Super+F1–F5 to workspaces.
## Close window

On Base (also inherited by Lower), double-tap the physical **=** key to send
**Alt+F4** and close the active window. Each tap must be shorter than 250 ms,
and the second press must start within 250 ms of the first release.
A single tap types `=` after the double-tap window expires; holding types `=`.
To type `==`, pause longer than 250 ms between taps. Gaming is unchanged.

## Magic

| Shortcut | Action |
|---|---|
| Magic+T | RGB on/off |
| Magic+G | Next RGB effect |
| Magic+R / F | RGB brightness up/down |
| Magic+E / D | RGB hue up/down |
| Magic+Q / A | RGB speed up/down |
| Magic+Space / left Ctrl | Select Bluetooth profile 0 / 1 and prefer Bluetooth |
| Magic+left Shift / left Alt | Select Bluetooth profile 2 / 3 and prefer Bluetooth |
| Magic+left GUI | Prefer USB output |
| Magic+F1 | Clear the selected host Bluetooth bond |
| Magic+Print Screen | Clear all host Bluetooth bonds |
| Magic+Esc / Quote | Enter the left / right bootloader |
| Magic+Grave / Page Up | Reset the left / right half |

Magic+S and Magic+W are unassigned: there is no separate background-animation
toggle or lighting power-policy control. RGB uses MoErgo's effects and status
indicators; there are no custom per-key Lower highlights or palette controls.
RGB starts off according to the board defaults. Previously saved lighting state
can take precedence; Magic+T toggles it. See [MoErgo's RGB guide](https://docs.moergo.com/glove80-user-guide/rgb/).
