#!/usr/bin/env python3
"""Copy a combined MoErgo UF2 to each Glove80 bootloader once, then exit."""
import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone

HALVES = {"GLV80LHBOOT": ("LH", 0x9807B007), "GLV80RHBOOT": ("RH", 0x9808B007)}


def validate_firmware(data):
    if not data or len(data) % 512:
        raise ValueError("Firmware must be a complete combined UF2 (512-byte blocks)")
    groups = {family: [] for _, family in HALVES.values()}
    for offset in range(0, len(data), 512):
        block = data[offset:offset + 512]
        m0, m1, flags, address, size, number, total, family = struct.unpack_from("<8I", block)
        if (m0, m1, struct.unpack_from("<I", block, 508)[0]) != (0x0A324655, 0x9E5D5157, 0x0AB16F30):
            raise ValueError("Invalid UF2 block header")
        if flags != 0x2000 or family not in groups or size != 256:
            raise ValueError("Expected MoErgo Glove80 application UF2 families and 256-byte payloads")
        if address < 0x26000 or address + size > 0xEC000 or address % 256:
            raise ValueError("UF2 writes outside the Glove80 application partition")
        groups[family].append((number, total, address))
    for blocks in groups.values():
        if not blocks or sorted(blocks) != [(i, len(blocks), 0x26000 + 256 * i) for i in range(len(blocks))]:
            raise ValueError("UF2 must contain complete, non-duplicated images for both halves")


def volumes():
    result = subprocess.run(
        ["lsblk", "--json", "--paths", "--output", "NAME,LABEL,FSTYPE,MOUNTPOINTS,TRAN"],
        check=True, capture_output=True, text=True,
    )
    found = []

    def visit(device, transport=None):
        transport = device.get("tran") or transport
        if device.get("label") in HALVES and device.get("fstype") == "vfat" and transport == "usb":
            mounts = [Path(p) for p in device.get("mountpoints", []) if p]
            if len(mounts) > 1:
                raise ValueError(f"Multiple mountpoints for {device['label']}")
            if mounts:
                found.append((device["label"], device["name"], mounts[0]))
        for child in device.get("children", []):
            visit(child, transport)

    for device in json.loads(result.stdout)["blockdevices"]:
        visit(device)
    labels = [label for label, _, _ in found]
    if len(labels) != len(set(labels)):
        raise ValueError("Multiple bootloader volumes for the same half; disconnect the extra device")
    return found


def open_bootloader(label, mount):
    if not mount.is_mount():
        raise ValueError(f"{mount} is no longer a mounted volume")
    directory = os.open(mount, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fd = os.open("INFO_UF2.TXT", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        with os.fdopen(fd, "r") as info:
            # Some official bootloaders encode line endings as literal escapes.
            content = info.read(4096).replace("\\r\\n", "\n")
        half = HALVES[label][0]
        if not re.search(rf"^Board-ID:\s*Glove80-{half}-rev\S+\s*$", content, re.M):
            raise ValueError(f"{label}: INFO_UF2.TXT does not identify a Glove80 {half} bootloader")
        return directory
    except BaseException:
        os.close(directory)
        raise


def transfer(directory, data, recovery, half):
    # Save the device's current flash image before the first firmware write.
    fd = os.open("CURRENT.UF2", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
    with os.fdopen(fd, "rb") as current:
        previous = current.read()
    if not previous or len(previous) % 512:
        raise ValueError(f"{half}: cannot save a complete CURRENT.UF2 recovery image")
    for offset in range(0, len(previous), 512):
        m0, m1, _, _, size, number, total, _ = struct.unpack_from("<8I", previous, offset)
        if ((m0, m1, struct.unpack_from("<I", previous, offset + 508)[0])
                != (0x0A324655, 0x9E5D5157, 0x0AB16F30)
                or size != 256 or number != offset // 512 or total != len(previous) // 512):
            raise ValueError(f"{half}: CURRENT.UF2 is incomplete or invalid; firmware not copied")
    backup = recovery / f"before-{half}.uf2"
    with backup.open("xb") as output:
        output.write(previous)
        output.flush()
        os.fsync(output.fileno())
    fd = os.open("glove80.uf2", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o644, dir_fd=directory)
    written = 0
    try:
        while written < len(data):
            count = os.write(fd, data[written:written + 65536])
            if count == 0:
                raise OSError("Firmware write made no progress")
            written += count
        os.fsync(fd)
    except OSError as error:
        # A UF2 bootloader may disconnect during the final flush. Never accept
        # an interrupted data write, and require disappearance in the caller.
        if written != len(data) or error.errno not in (errno.EIO, errno.ENODEV, errno.ENOENT):
            raise
    finally:
        try:
            os.close(fd)
        except OSError as error:
            if written != len(data) or error.errno not in (errno.EIO, errno.ENODEV):
                raise


def wait_for_reboot(volume, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if volume not in volumes():
            return
        time.sleep(0.5)
    raise ValueError(f"{volume[0]} still mounted after copying; transfer was not confirmed")


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firmware", nargs="?", type=Path, default=root / "result/glove80.uf2")
    parser.add_argument("--dry-run", action="store_true", help="Check the image and current volumes without writing")
    args = parser.parse_args()
    data = args.firmware.read_bytes()
    validate_firmware(data)
    digest = hashlib.sha256(data).hexdigest()
    print(f"Firmware: {args.firmware.resolve()} ({len(data):,} bytes)\nSHA256: {digest}", flush=True)
    if args.dry_run:
        for label, _, mount in volumes():
            os.close(open_bootloader(label, mount))
            print(f"Verified {label}: {mount}; would back up CURRENT.UF2 and copy firmware")
        print("Dry run: no files written; no firmware flashed.")
        return
    recovery = root / "artifacts" / ("autodrop-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"))
    recovery.mkdir(parents=True)
    (recovery / "glove80.uf2").write_bytes(data)
    (recovery / "SHA256SUMS").write_text(f"{digest}  glove80.uf2\n")
    print(f"Recovery directory: {recovery}\nWaiting for mounted GLV80LHBOOT / GLV80RHBOOT. Ctrl+C stops.", flush=True)
    completed = set()
    while len(completed) < 2:
        for volume in volumes():
            label, _, mount = volume
            if label in completed:
                continue
            directory = open_bootloader(label, mount)
            try:
                print(f"{label}: saving recovery image, then copying firmware...", flush=True)
                transfer(directory, data, recovery, HALVES[label][0])
            finally:
                os.close(directory)
            wait_for_reboot(volume)
            completed.add(label)
            (recovery / "completed.txt").write_text("\n".join(sorted(completed)) + "\n")
            print(f"{label}: copy complete; bootloader disappeared ({len(completed)}/2).", flush=True)
        time.sleep(0.5)
    print("Both halves transferred. Check typing and pairing; this does not verify physical behavior.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped; completed halves are recorded in the recovery directory.", file=sys.stderr)
        sys.exit(130)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Autodrop stopped: {error}", file=sys.stderr)
        sys.exit(1)
