# Controls

Key names below refer to physical QWERTY positions. The complete bindings are in
`config/runtime.toml`; open it in the editor to inspect individual keys.

## Layers

| Layer | Use |
|---|---|
| Base | QWERTY typing and function keys |
| Lower | Navigation, keypad, media and display-brightness controls |
| Magic | Lighting, Bluetooth profiles and firmware controls |
| Gaming | Dedicated gaming bindings |

Hold Lower or Magic to use that layer. Press **B + Right Arrow** together within
50 ms to toggle Gaming. In Gaming, the same physical positions are **F + C**.
Toggle back to Base before using Magic.

## Tap and hold

On Base, F1–F5 have a 200 ms hold threshold:

- Tap: send the function key.
- Hold: press Super, tap the corresponding function key once, then release Super.
  Release and hold again to trigger another shortcut.

Workspace switching requires the host to bind Super+F1–F5 to workspaces.
The keyboard sends these shortcuts; it does not configure the desktop.

The remaining Base tap/holds use the same threshold:

| Key | Tap | Hold |
|---|---|---|
| Print Screen | Print Screen | Super+Print Screen |
| 1 | 1 | Shift+1 |
| 7 | 7 | Shift+Slash |

## Close window

On Base (also inherited by Lower), double-tap the physical **=** key to send
**Alt+F4** and close the active window. Each tap must be shorter than 250 ms,
and the second press must start within 250 ms of the first release.
A single tap types `=` after the double-tap window expires; holding types `=`.
To type `==`, pause longer than 250 ms between taps. Gaming is unchanged.

## Magic

| Shortcut | Action |
|---|---|
| Magic+T | All lighting on/off; Magic can still show status indicators |
| Magic+G | Next background animation |
| Magic+S | Background animation on/off |
| Magic+R / F | Master brightness up/down for all LEDs |
| Magic+E / D | Next/previous palette |
| Magic+Q / A | Animation speed up/down |
| Magic+W | Cycle always-on / always-off / USB-powered-only lighting policy |
| Magic+Space / left Ctrl | Select Bluetooth slot 0 / 1 |
| Magic+left Shift / left Alt | Select Bluetooth slot 2 / 3 |
| Magic+left GUI | Prefer USB output |
| Magic+F1 | Clear the selected Bluetooth slot's host bond |
| Magic+Print Screen | Clear all host Bluetooth bonds |
| Magic+Esc / Quote | Enter the left / right bootloader |

See [Bluetooth pairing](first-install.md#pair-bluetooth) and
[firmware recovery](first-install.md#recover) for connection and recovery steps.

## Lighting

Lower adds eight highlights over the background animation: yellow for display
brightness, blue for volume/mute, and green for media controls. Base and Gaming
add no layer highlights; the selected background animation can still run.
Use Magic+S to disable only the animation while retaining layer highlights.
Choose the always-on policy to allow lighting while wireless.

Magic+R/F controls brightness across animations, Lower highlights and Magic
indicators. Animation intensity is set to its maximum so master brightness is
the shared adjustment. The pinned firmware resets master brightness to 255 on
boot; the level selected during use does not survive a power cycle.

While Magic is held:

- Each outer column shows a five-segment battery bar for its half.
- T shows the lighting policy: green for always-on, red for always-off, blue for
  USB-powered-only.
- Bluetooth thumb indicators are blue for the selected slot and green when
  that slot is connected and carrying keyboard output.
