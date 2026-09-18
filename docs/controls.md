# Controls

Base is your QWERTY layout. Gaming preserves all 80 source bindings. Lower also
preserves its supplied bindings. **Physical B + Right Arrow** toggles Gaming;
those same positions are **F + C** while Gaming is active. Press within 50 ms.
Exit Gaming before using Magic, since Gaming intentionally replaces that key.

The eight Base tap/holds retain their explicit outputs: F1–F5 / GUI+F1–F5,
Print Screen / GUI+Print Screen, 1 / Shift+1, and 7 / Shift+Slash.
RMK uses a 200 ms hold threshold; matching outputs does not prove identical ZMK
rollover/timing. Test ordinary typing before relying on them.

## Magic

Names below refer to the physical QWERTY labels.

| Shortcut | Action |
|---|---|
| Magic+T | All lighting on/off; holding Magic still permits its status view |
| Magic+G | Next background animation |
| Magic+S | Animation on/off, keeping meaningful highlights |
| Magic+R / F | Master brightness up/down for all LEDs (0–255) |
| Magic+E / D | Next/previous palette |
| Magic+Q / A | Animation speed up/down |
| Magic+W | Cycle lighting always-on / always-off / USB-powered-only |
| Magic+Space / left Ctrl | Select Bluetooth slot 0 / 1 |
| Magic+left Shift / left Alt | Select Bluetooth slot 2 / 3 |
| Magic+left GUI | Prefer USB output |
| Magic+F1 | Clear the selected host's Bluetooth bond |
| Magic+Print Screen | Clear all host Bluetooth bonds |
| Magic+Esc / Quote | Left / right bootloader |

The Magic controls differ from ZMK: palettes replace continuous hue, and W/S
replace saturation controls with output policy and animation toggle. These
changes enable highlights and effects to be controlled independently.
Bluetooth pairing and recovery details are in [first install](first-install.md).

## Lighting

Lower has eight highlights: yellow screen brightness, blue volume/mute, and
green media controls. They overlay the normal effect instead of selecting a
special layer effect. Other layers add no whole-keyboard mask. Gaming's black
editor decorations do not add LEDs; an enabled background animation still runs.
Magic+S enables or disables the animation without removing layer highlights.
Magic+R/F scales all RGB together: animations, Lower highlights and Magic
indicators. Animation intensity is kept at 255 when enabled, leaving master
brightness as the shared adjustment. Magic+T controls all lighting. Magic+W cycles between
always-on, always-off and USB-powered-only; the T indicator shows green, red
or blue respectively. Choose always-on for Lower highlights while wireless.

Lower highlights retain their original relative intensities, and Magic
indicators retain their status colors; master brightness scales both.
The pinned firmware resets master brightness to 255 on boot; the common
control works during use, but its chosen level does not survive a power cycle.

Holding Magic shows a five-segment battery bar on each outer column. T shows
lighting policy (green on, red off, blue USB-only). Bluetooth thumb indicators
are blue for selected and green for connected and carrying typing. These are
our RMK status indicators, not a reproduction of MoErgo's original display.
Their physical behavior remains part of the hardware trial.
