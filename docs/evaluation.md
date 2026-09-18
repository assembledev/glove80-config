# Evaluation

**Decision: proceed with a reversible RMK hardware trial. Do not yet call this a
qualified daily-use keyboard.** The project is now usable for offline editing
and has automated checks. Both halves are flashed; USB and Bluetooth
configuration transactions and split lighting synchronization have passed.
Typing latency, sleep/wake and battery endurance remain unmeasured.

## Fit for this keyboard

The requirement is QWERTY and Gaming first, comfortable wireless use with USB
charging available, and meaningful highlights alongside normal RGB effects.
MoErgo's PR36 layer effect replaces the normal effect; it does not provide that
composition. The pinned Colonel firmware has separate effect and scene inputs,
wireless split support, and a runtime configuration interface. This is a
reasonable fit, with a higher maintenance burden than staying on MoErgo ZMK.

We use `moergo-rmk` for the firmware and its own RMK fork, plus `rynkbench` for
editing. Colonel's personal `moergo-config` repository supplied examples, not
our configuration authority. The dependency boundaries and update procedure
are in [maintenance](firmware.md).

## Checks performed, 2026-09-18

| Area | Evidence | What it does not establish |
|---|---|---|
| Layout migration | Independent source comparison passed all 240 Base/Lower/Gaming positions, eight tap/hold outputs, two scoped Gaming combos and the eight Lower LED positions | Physical scan mapping, rollover and tap/hold feel |
| File compatibility | The CLI validates the runtime; both WASM codecs build from the exact firmware/RMK pins | Device transport reliability |
| Visual editor model | 579 tests pass across 70 suites, including this layout's codec and full offline-workspace round trips; TypeScript and production build pass | A visual/browser usability review; no browser was available in this environment |
| Save and sync | 21 project tests pass: backups, validation, concurrent saves, outside edits, disconnection, failed preview/readback transport forwarding and failure isolation, and a static server with no project write API | Exhaustive transport failure testing on hardware |
| Hardware connection | Both halves flashed; USB and BLE apply/readback passed; split lighting reported healthy with matching digests | Long-term reconnect reliability, complete typing and sleep/wake qualification |
| Launcher | Static-server test serves editor assets while rejecting project access and writes | A rendered interactive browser session |
| Firmware | Both halves rebuilt from clean pinned sources; UF2 checksums, half-specific families, application ranges and compiled-config hash pass | Flashing, BLE reconnection, latency, sleep/wake or battery life |

Reproduce routine checks with `./keyboard check`, editor tests/build with
`./keyboard build-editor`. The original-source comparison is a migration audit,
not a restriction on future deliberate layout edits: inside the project shell,
run `python3 scripts/evaluate.py --migration`. It requires the private original
JSON in `backups/original/`. Test/build logs are retained in `.cache/`; hardware
results belong in `artifacts/`.

## Dependency suitability

Rynkbench's existing offline Open/Download TOML and live WebHID editing cover
layout editing without modifying its source. It lacks direct save into this
repository. That is a workflow limitation, not evidence that its keyboard
support requires patching. The supported file workflow is explicit in the
README; live changes can be captured with `pull`.

There are no downstream editor patches or custom editor write APIs. Keeping a
private editor variant solely for automatic file opening and direct repository
saving was unnecessary maintenance. If direct file saving becomes a requirement,
reassess the editor or use an upstream-supported feature rather than recreate
that variant.

Master brightness now scales animations, highlights and indicators together.
The pinned firmware resets that level on reboot; see [controls](controls.md). Apply still requires a
successful preview and readback, and protects against unsynced device changes.

## Remaining qualifications

The firmware is a rapidly changing community fork. Staying pinned prevents a
silent update; it does not supply a stability guarantee. The fresh left image has 24,832 bytes of
free application space, so future firmware updates must repeat size and
partition checks.

A 300-second idle sleep timeout is compiled. The split radio timing retains
Colonel's responsive defaults. Neither proves low power consumption. LED load,
right-half wake and reconnection need the actual measurements in
[first install](first-install.md). No battery lifetime claim is made.

The original eight Base tap/holds have matching outputs, but their 200 ms RMK
behavior is a migration choice, not proven ZMK timing parity. Magic's palette,
policy and animation controls intentionally differ; see [controls](controls.md).

Pre-flash dumps of both halves are retained privately, but neither is a verified
ZMK rollback image. Recovery-image verification and the remaining hardware trial
checks are still open. Detailed device captures remain in ignored `artifacts/`.
