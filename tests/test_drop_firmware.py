import errno
import importlib.util
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

script = Path(os.environ.get("GLOVE80_DROPPER", Path(__file__).resolve().parents[1] / "scripts/drop-firmware.py"))
spec = importlib.util.spec_from_file_location("dropper", script)
dropper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dropper)


def block(family, number=0, total=1, address=0x26000):
    return (struct.pack("<8I", 0x0A324655, 0x9E5D5157, 0x2000, address, 256, number, total, family)
            + bytes(476) + struct.pack("<I", 0x0AB16F30))


IMAGE = block(0x9807B007) + block(0x9808B007)


class DropFirmwareTests(unittest.TestCase):
    def test_only_complete_combined_application_images_accepted(self):
        dropper.validate_firmware(IMAGE)
        for invalid in [b"", IMAGE[:-1], IMAGE[:512], IMAGE + IMAGE[:512],
                        bytes(1024), block(0xADA52840) + IMAGE[512:],
                        block(0x9807B007, total=2) + IMAGE[512:],
                        block(0x9807B007, address=0xEC000) + IMAGE[512:]]:
            with self.subTest(image=invalid[:32]), self.assertRaises(ValueError):
                dropper.validate_firmware(invalid)

    def test_discovery_requires_usb_fat_labels_and_handles_partitions(self):
        devices = {"blockdevices": [
            {"name": "/dev/sda", "tran": "usb", "children": [
                {"name": "/dev/sda1", "label": "GLV80LHBOOT", "fstype": "vfat", "mountpoints": ["/media/left"]}]},
            {"name": "/dev/sdb", "tran": "usb", "label": "OTHER", "fstype": "vfat", "mountpoints": ["/media/other"]},
            {"name": "/dev/sdc", "tran": "sata", "label": "GLV80RHBOOT", "fstype": "vfat", "mountpoints": ["/media/wrong"]},
            {"name": "/dev/sdd", "tran": "usb", "label": "GLV80RHBOOT", "fstype": "vfat", "mountpoints": [None]},
        ]}
        with patch.object(dropper.subprocess, "run") as run:
            run.return_value.stdout = json.dumps(devices)
            self.assertEqual(dropper.volumes(), [("GLV80LHBOOT", "/dev/sda1", Path("/media/left"))])
            devices["blockdevices"].append(devices["blockdevices"][0])
            run.return_value.stdout = json.dumps(devices)
            with self.assertRaises(ValueError):
                dropper.volumes()

    def test_mount_and_board_identity_checked_before_write(self):
        with tempfile.TemporaryDirectory() as directory:
            mount = Path(directory)
            (mount / "INFO_UF2.TXT").write_text("Board-ID: Glove80-LH-revH\n")
            with self.assertRaises(ValueError):
                dropper.open_bootloader("GLV80LHBOOT", mount)
            with patch.object(Path, "is_mount", return_value=True):
                fd = dropper.open_bootloader("GLV80LHBOOT", mount)
                os.close(fd)
                with self.assertRaises(ValueError):
                    dropper.open_bootloader("GLV80RHBOOT", mount)
                (mount / "INFO_UF2.TXT").write_text("Model: Glove80 v1 LH\\r\\nBoard-ID: Glove80-LH-revH\\r\\n")
                fd = dropper.open_bootloader("GLV80LHBOOT", mount)
                os.close(fd)

    def test_transfer_preserves_recovery_and_writes_exact_combined_image(self):
        with tempfile.TemporaryDirectory() as directory:
            mount = Path(directory) / "volume"
            recovery = Path(directory) / "recovery"
            mount.mkdir(); recovery.mkdir()
            original = block(0x9807B007)
            (mount / "CURRENT.UF2").write_bytes(original)
            fd = os.open(mount, os.O_RDONLY | os.O_DIRECTORY)
            try:
                dropper.transfer(fd, IMAGE, recovery, "LH")
            finally:
                os.close(fd)
            self.assertEqual((recovery / "before-LH.uf2").read_bytes(), original)
            self.assertEqual((mount / "glove80.uf2").read_bytes(), IMAGE)

    def test_missing_recovery_or_existing_target_prevents_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            mount = Path(directory)
            fd = os.open(mount, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with self.assertRaises(FileNotFoundError):
                    dropper.transfer(fd, IMAGE, mount, "LH")
                self.assertFalse((mount / "glove80.uf2").exists())
                (mount / "CURRENT.UF2").write_bytes(block(0x9807B007))
                (mount / "glove80.uf2").symlink_to(mount / "CURRENT.UF2")
                with self.assertRaises(FileExistsError):
                    dropper.transfer(fd, IMAGE, mount, "LH")
                self.assertEqual((mount / "CURRENT.UF2").read_bytes(), block(0x9807B007))
            finally:
                os.close(fd)

    def test_final_flush_disconnect_allowed_but_partial_write_is_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            mount = Path(directory)
            (mount / "CURRENT.UF2").write_bytes(block(0x9807B007))
            fd = os.open(mount, os.O_RDONLY | os.O_DIRECTORY)
            try:
                with patch.object(dropper.os, "fsync", side_effect=[None, OSError(errno.EIO, "disconnected")]):
                    dropper.transfer(fd, IMAGE, mount, "LH")
                (mount / "glove80.uf2").unlink()
                with patch.object(dropper.os, "write", side_effect=OSError(errno.EIO, "partial")):
                    with self.assertRaises(OSError) as failure:
                        dropper.transfer(fd, IMAGE, mount, "RH")
                    self.assertEqual(failure.exception.errno, errno.EIO)
            finally:
                os.close(fd)

    def test_copy_is_not_confirmed_until_volume_disappears(self):
        volume = ("GLV80LHBOOT", "/dev/sda", Path("/media/left"))
        with patch.object(dropper, "volumes", side_effect=[[volume], []]), patch.object(dropper.time, "sleep"):
            dropper.wait_for_reboot(volume)
        with self.assertRaises(ValueError):
            dropper.wait_for_reboot(volume, timeout=0)

    def test_default_uses_latest_build_and_each_half_is_copied_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "result").mkdir()
            (root / "result/glove80.uf2").write_bytes(IMAGE)
            left, right = root / "left", root / "right"
            for mount, half in [(left, "LH"), (right, "RH")]:
                mount.mkdir()
                (mount / "INFO_UF2.TXT").write_text(f"Board-ID: Glove80-{half}-revH\n")
                (mount / "CURRENT.UF2").write_bytes(block(0x9807B007 if half == "LH" else 0x9808B007))
            lh = ("GLV80LHBOOT", "/dev/sda", left)
            rh = ("GLV80RHBOOT", "/dev/sdb", right)
            with patch.object(dropper, "__file__", str(root / "scripts/drop-firmware.py")), \
                 patch.object(dropper.sys, "argv", ["drop-firmware"]), \
                 patch.object(Path, "is_mount", return_value=True), \
                 patch.object(dropper, "volumes", side_effect=[[lh], [lh, rh]]), \
                 patch.object(dropper, "wait_for_reboot") as reboot, \
                 patch.object(dropper.time, "sleep"), patch("builtins.print"):
                dropper.main()
            self.assertEqual(reboot.call_count, 2)
            for mount in [left, right]:
                self.assertEqual((mount / "glove80.uf2").read_bytes(), IMAGE)
            recovery, = (root / "artifacts").iterdir()
            self.assertEqual((recovery / "completed.txt").read_text(), "GLV80LHBOOT\nGLV80RHBOOT\n")

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "result").mkdir()
            (root / "result/glove80.uf2").write_bytes(IMAGE)
            with patch.object(dropper, "__file__", str(root / "scripts/drop-firmware.py")), \
                 patch.object(dropper.sys, "argv", ["drop-firmware", "--dry-run"]), \
                 patch.object(dropper, "volumes", return_value=[]), patch("builtins.print"):
                dropper.main()
            self.assertFalse((root / "artifacts").exists())


if __name__ == "__main__":
    unittest.main()
