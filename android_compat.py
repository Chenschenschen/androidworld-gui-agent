"""Work around AndroidEnv 1.2.3's temporary APK issue on Windows/Python 3.11."""

from pathlib import Path
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET


def enable_windows_compat():
    """Give ADB a closed file when AndroidEnv requests installation from bytes.

    AndroidEnv keeps a NamedTemporaryFile open during installation. On Windows,
    Python 3.11 prevents ADB from opening that file. This adapter changes only
    the file handoff; AndroidEnv still performs the actual installation.
    """
    if sys.platform != "win32" or sys.version_info >= (3, 12):
        return

    from android_env.components import adb_call_parser
    from android_env.proto import adb_pb2

    original_install = adb_call_parser.AdbCallParser._install_apk
    temp_root = Path(__file__).resolve().parent / ".tools" / "tmp"
    temp_root.mkdir(parents=True, exist_ok=True)

    def install_from_closed_file(self, request, timeout=None):
        """Convert an APK byte request to a file request, then delegate it."""
        if request.install_apk.WhichOneof("location") != "blob":
            return original_install(self, request, timeout)

        # The directory remains available until ADB finishes installing the APK.
        with tempfile.TemporaryDirectory(dir=temp_root) as folder:
            apk_path = Path(folder) / "app.apk"
            apk_path.write_bytes(request.install_apk.blob.contents)
            adapted = adb_pb2.AdbRequest()
            adapted.CopyFrom(request)
            # Protobuf's oneof replaces the byte payload with the file path.
            adapted.install_apk.filesystem.path = str(apk_path)
            return original_install(self, adapted, timeout)

    # A narrow runtime adapter keeps the downloaded source and .venv unchanged.
    adb_call_parser.AdbCallParser._install_apk = install_from_closed_file


def enable_fresh_xml():
    """Prevent reused XML files from masquerading as a fresh UIAutomator observation."""
    from android_world.env import adb_utils

    def fresh_dump(env, timeout_sec=30):
        """Check dump/read responses and parse a unique generated XML before returning."""
        remote = f"/sdcard/autoglm_ui_{uuid.uuid4().hex}.xml"
        try:
            # A cold-starting app can briefly report "null root node" and write
            # nothing (observed on a fresh emulator's first Contacts setup). Retry
            # that transient state a bounded number of times; still never read
            # an unconfirmed (possibly stale) file.
            for attempt in range(3):
                dumped = adb_utils.issue_generic_request(f"shell uiautomator dump {remote}", env, timeout_sec=timeout_sec)
                adb_utils.check_ok(dumped, "UIAutomator dump failed")
                if remote in dumped.generic.output.decode("utf-8", errors="replace"):
                    break
                time.sleep(1)
            else:
                raise RuntimeError("UIAutomator did not confirm writing this observation")
            read = adb_utils.issue_generic_request(f"shell cat {remote}", env, timeout_sec=timeout_sec)
            adb_utils.check_ok(read, "UIAutomator XML read failed")
            xml = read.generic.output.decode("utf-8")
            if ET.fromstring(xml).tag != "hierarchy":
                raise RuntimeError("Invalid UIAutomator hierarchy")
            return xml
        finally:
            # Remove only this invocation's generated temporary observation.
            adb_utils.issue_generic_request(f"shell rm -f {remote}", env, timeout_sec=timeout_sec)

    adb_utils.uiautomator_dump = fresh_dump
