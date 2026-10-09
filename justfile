# Show the available commands.
default:
    @just --list

# Check the keymap and command syntax without compiling firmware.
check:
    @./keyboard check

# Build MoErgo's combined image for both halves on the flashing computer.
build-firmware:
    @./keyboard build-firmware

# Wait for bootloader volumes and copy the current build to both halves.
drop-firmware:
    @./keyboard drop-firmware
