# Validation and limitations

Automated checks verify configuration encoding, file operations and build
outputs. Hardware checks verify the behavior of the installed firmware. Passing
one does not establish the other.

## Automated checks

Run these from the project environment:

| Command | Coverage |
|---|---|
| `nix flake check` | Transaction and build-failure regressions, shell/recipe syntax, Nix formatting |
| `just check` | Runtime validation, project regressions, dependency pins, and checksums/partition bounds of locally available firmware bundles |
| `just build-editor` | Pinned WASM codecs, TypeScript, editor tests, layout round trips, workspace macro encoding, and the production editor build |
| `just build-firmware` | Both firmware images, bundle manifest and checksums |

`just check` can pass without a local firmware bundle; it reports that images
need building. It does not connect to the keyboard. An apply verifies the
configuration read back from the device, not the resulting physical key events.

The optional `python3 scripts/evaluate.py --migration` compares against a private
original layout in `backups/original/source-layout.json`. It is an import audit,
not a check of the current customized layout or a fresh-clone prerequisite.

## Hardware checks

Repeat these after firmware changes. Record the source revisions, build bundle,
connection type, procedure and observed result in an ignored file under
`artifacts/`. Record failed and untested cases explicitly.

| Area | Check |
|---|---|
| Typing | Exercise every key on both halves, including quick taps, long holds and overlapping keys |
| Workspace shortcuts | Tap F1–F5 normally; hold each past the threshold and keep holding to check that the shortcut fires only once and Super is released |
| Gaming | Enter and leave Gaming repeatedly; check the gaming bindings and toggle positions |
| Wireless | Type from both halves with USB disconnected; reconnect after host and keyboard power cycles |
| Sleep | Wait beyond the configured idle timeout; test wake from each half and check the first keystroke and split connection |
| Persistence | Power-cycle both halves and compare bindings, layer metadata, scenes, effects and output policy |
| Lighting | Check Lower highlights, master brightness, Magic battery bars and Bluetooth indicators on the physical keys |
| Battery | Measure both halves over normal use and idle periods, recording duration and lighting settings |

Battery percentages are coarse estimates. Use measured intervals to compare
settings; do not infer battery lifetime from a short sample. Keep a tested
recovery image available; see [recovery](first-install.md#recover).

## Known limits

USB and Bluetooth configuration apply/readback and split lighting synchronization
have been exercised on the development keyboard. Full key coverage, sustained
reconnect reliability, sleep/wake behavior, typing latency and battery endurance
are not comprehensively qualified. The workspace macros have encoding and device
readback checks; those checks alone do not confirm physical shortcut behavior.

Master brightness resets on boot; its behavior is documented with the
[lighting controls](controls.md#lighting). Browser device access depends on the
available transport APIs; see [live editing](firmware.md#live-editing).

Pinned dependencies make builds reproducible from specified sources. Updates
still require the automated and hardware checks above; follow the
[dependency update procedure](firmware.md#dependency-updates).
