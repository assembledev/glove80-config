# Show available commands.
default:
    @just --list

# Open the visual editor; keep this running until finished.
edit *args:
    @./keyboard edit {{args}}

# Import a downloaded editor file, validating and backing up first.
save file:
    @./keyboard save {{quote(file)}}

# Save current keyboard settings into this project (Bluetooth by default).
pull *args="--ble":
    @./keyboard pull {{args}}

# Apply saved settings with backup, conflict checks, and verified readback.
apply *args="--ble":
    @./keyboard apply {{args}}

# Compare the saved configuration with the keyboard.
diff *args="--ble":
    @./keyboard diff {{args}}

# Back up current keyboard settings without changing the project.
backup *args="--ble":
    @./keyboard backup {{args}}

# Validate the saved configuration offline.
validate:
    @./keyboard validate

# Run configuration, transaction, dependency, and firmware-image checks.
check:
    @./keyboard check

# Show local build and configuration readiness.
status:
    @./keyboard status

# Initialize pinned submodules after cloning.
init:
    @./keyboard init

# Rebuild the visual editor and run its tests.
build-editor:
    @./keyboard build-editor

# Rebuild both firmware images; does not flash the keyboard.
build-firmware:
    @./keyboard build-firmware

# Rebuild the upstream CLI.
build-tools:
    @./keyboard build-tools

# Advanced upstream CLI (can bypass project safeguards).
control *args:
    @./keyboard control {{args}}

# Format the project flake.
fmt:
    @nixfmt flake.nix
