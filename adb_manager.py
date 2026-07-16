# ADB Execution & Platform Tools Downloader Manager for Warp Transfer

import os
import re
import sys
import zipfile
import shutil
import subprocess
import requests
from PyQt6.QtCore import QObject, pyqtSignal, QThread

PLATFORM_TOOLS_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"


class DownloadWorker(QThread):
    # Signals for download progress
    progress = pyqtSignal(int, int)  # bytes_downloaded, total_bytes
    finished = pyqtSignal(bool, str) # success, message

    def __init__(self, dest_dir):
        super().__init__()
        self.dest_dir = dest_dir

    def run(self):
        try:
            os.makedirs(self.dest_dir, exist_ok=True)
            zip_path = os.path.join(self.dest_dir, "platform_tools.zip")

            # Download zip file with stream chunk tracking
            response = requests.get(PLATFORM_TOOLS_URL, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.progress.emit(downloaded, total_size)

            # Extract zip file
            self.progress.emit(total_size, total_size) # Mark as downloaded

            # Use zipfile to extract directly to dest_dir
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.dest_dir)

            # Clean up zip file
            if os.path.exists(zip_path):
                os.remove(zip_path)

            self.finished.emit(True, "Platform tools setup completed successfully.")
        except Exception as e:
            self.finished.emit(False, str(e))


class AdbManager(QObject):
    device_status_changed = pyqtSignal(str, str)  # status, device_id/name

    def __init__(self):
        super().__init__()
        # Determine application directory
        if getattr(sys, 'frozen', False):
            self.app_dir = os.path.dirname(sys.executable)
        else:
            self.app_dir = os.path.dirname(os.path.abspath(__file__))

        self.bin_dir = os.path.join(self.app_dir, "bin")
        self.adb_dir = os.path.join(self.bin_dir, "platform-tools")
        self.adb_path = os.path.join(self.adb_dir, "adb.exe")

        self.current_status = "disconnected"
        self.current_device = ""
        # Raw ADB serial for whatever device check_devices() last saw, kept
        # separate from current_device (which is the human-friendly model
        # name for "connected" status). MainWindow needs the stable serial
        # -- not the display name -- as the dict key for config["known_devices"]
        # (Phase 4, localsend_parity_plan.md), since a friendly name isn't a
        # reliable identifier and "offline"/"unauthorized" states report the
        # serial as `device` anyway while "connected" reports the model name.
        self.current_device_id = ""

        # When more than one device/emulator is attached, ADB refuses to
        # target one implicitly. Once the user picks a device via the
        # device-picker dialog, every targetable command is automatically
        # scoped to it with "-s <id>" (see run_adb_cmd's use_target flag).
        self.target_device_id = None

    def is_adb_installed(self) -> bool:
        return os.path.exists(self.adb_path)

    def start_download(self) -> DownloadWorker:
        self.worker = DownloadWorker(self.bin_dir)
        return self.worker

    def set_target_device(self, device_id: str):
        """Pin all future targetable ADB commands to a specific device.
        Called after the user resolves a multi-device situation via the
        device picker."""
        self.target_device_id = device_id

    def clear_target_device(self):
        self.target_device_id = None

    def run_adb_cmd(self, args: list, timeout: int = 10, use_target: bool = True) -> tuple:
        """Executes an adb command silently on Windows with hidden window flags.

        use_target=True (default) automatically inserts "-s <target_device_id>"
        right after the adb binary when a target has been pinned via
        set_target_device(). Pass use_target=False for device-agnostic
        commands (devices, start-server, kill-server, pair, connect) or when
        the caller has already supplied its own explicit "-s" targeting.
        """
        if not self.is_adb_installed():
            return -1, "", "ADB binary not found."

        cmd = [self.adb_path]
        if use_target and self.target_device_id:
            cmd += ["-s", self.target_device_id]
        cmd += args

        try:
            # CREATE_NO_WINDOW prevents command prompt window flashes on Windows
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            # encoding/errors explicit rather than relying on subprocess's
            # text=True default, which falls back to the OS's preferred
            # codepage (cp1252 on this Windows setup). adb's stdout can
            # contain bytes outside cp1252 (e.g. non-ASCII filenames on the
            # phone), which previously crashed the subprocess reader thread
            # with UnicodeDecodeError -- silently killing that thread and
            # leaving result.stdout as None, which then blew up any caller
            # doing stdout.strip() (see scan_source_items in
            # transfer_engine.py). UTF-8 + errors='replace' means a stray
            # undecodable byte becomes a replacement character instead of
            # crashing the read entirely.
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=creationflags,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out."
        except Exception as e:
            return -1, "", str(e)

    def start_server(self):
        """Starts the ADB server silently in the background."""
        if self.is_adb_installed():
            self.run_adb_cmd(["start-server"], use_target=False)

    def kill_server(self):
        """Kills the ADB server."""
        if self.is_adb_installed():
            self.run_adb_cmd(["kill-server"], use_target=False)

    def list_all_devices(self) -> list:
        """Returns every attached device/emulator as a list of
        {"id", "status", "model"} dicts, regardless of how many are
        connected. Used by the device-picker dialog when check_devices()
        reports "multiple" so the user can choose one instead of being
        blocked outright."""
        if not self.is_adb_installed():
            return []

        code, stdout, _ = self.run_adb_cmd(["devices"], use_target=False)
        if code != 0:
            return []

        lines = [line.strip() for line in stdout.splitlines() if line.strip()]
        device_lines = lines[1:] if len(lines) > 0 else []

        results = []
        for dl in device_lines:
            parts = dl.split()
            if not parts:
                continue
            device_id = parts[0]
            state = parts[1] if len(parts) > 1 else "unknown"
            model = ""
            if state == "device":
                mcode, mstdout, _ = self.run_adb_cmd(
                    ["-s", device_id, "shell", "getprop", "ro.product.model"],
                    use_target=False
                )
                model = mstdout.strip() if mcode == 0 else ""
            results.append({"id": device_id, "status": state, "model": model or device_id})
        return results

    def check_devices(self) -> tuple:
        """Checks for connected devices and updates internal status."""
        if not self.is_adb_installed():
            return "disconnected", ""

        code, stdout, stderr = self.run_adb_cmd(["devices"], use_target=False)
        if code != 0:
            return "disconnected", ""

        lines = [line.strip() for line in stdout.splitlines() if line.strip()]
        # The first line of adb devices output is always 'List of devices attached'
        device_lines = lines[1:] if len(lines) > 0 else []

        if not device_lines:
            status, device = "disconnected", ""
            self.target_device_id = None
            self.current_device_id = ""
        elif len(device_lines) > 1:
            status, device = "multiple", f"{len(device_lines)} devices connected"
            self.current_device_id = ""
        else:
            parts = device_lines[0].split()
            device_id = parts[0]
            device_state = parts[1] if len(parts) > 1 else "unknown"
            self.current_device_id = device_id

            if device_state == "device":
                # Only one device is present, so it's the implicit target --
                # keep target_device_id in sync so run_adb_cmd's -s injection
                # stays harmless (adb ignores -s when it matches the sole device).
                self.target_device_id = device_id
                # Attempt to get a user-friendly product model name
                model_code, model_stdout, _ = self.run_adb_cmd(
                    ["-s", device_id, "shell", "getprop", "ro.product.model"], use_target=False
                )
                model_name = model_stdout.strip() if model_code == 0 else ""
                if not model_name:
                    model_name = device_id
                status, device = "connected", model_name
            elif device_state == "unauthorized":
                status, device = "unauthorized", device_id
            else:
                status, device = "offline", device_id

        if status != self.current_status or device != self.current_device:
            self.current_status = status
            self.current_device = device
            self.device_status_changed.emit(status, device)

        return status, device

    # ---------------------------------------------------------------
    # Wireless ADB (network) support
    # ---------------------------------------------------------------

    def enable_tcpip_mode(self, port: int = 5555) -> tuple:
        """Switches the currently-USB-connected device into TCP/IP listening
        mode. Required once (per boot) on Android <11 before a wireless
        adb connect will work. Returns (success, message)."""
        code, stdout, stderr = self.run_adb_cmd(["tcpip", str(port)], timeout=10)
        if code == 0:
            return True, stdout.strip() or f"Restarting in TCP/IP mode on port {port}."
        return False, stderr.strip() or "Failed to switch device into TCP/IP mode."

    def get_device_wifi_ip(self) -> str:
        """Best-effort lookup of the currently-connected device's Wi-Fi IP
        address, to prefill the wireless-connect dialog. Empty string if it
        can't be determined."""
        code, stdout, _ = self.run_adb_cmd(["shell", "ip", "-f", "inet", "addr", "show", "wlan0"], timeout=8)
        if code == 0:
            match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", stdout)
            if match:
                return match.group(1)
        return ""

    def pair_device(self, host_port: str, pairing_code: str) -> tuple:
        """Android 11+ wireless debugging pairing flow: `adb pair ip:port code`.
        The ip:port here is the *pairing* port shown on the phone's
        "Pair device with pairing code" screen, which is different from the
        regular connect port. Returns (success, message)."""
        code, stdout, stderr = self.run_adb_cmd(
            ["pair", host_port, pairing_code], timeout=15, use_target=False
        )
        output = (stdout + stderr).strip()
        if code == 0 and "Successfully paired" in output:
            return True, output
        return False, output or "Pairing failed -- check the IP:port and code, and that both devices are on the same network."

    def connect_wireless(self, host_port: str) -> tuple:
        """`adb connect ip:port` -- either after enable_tcpip_mode() on
        older Android, or after a successful pair_device() on Android 11+
        (using the regular Wireless debugging IP:port, not the pairing one).
        Returns (success, message)."""
        code, stdout, stderr = self.run_adb_cmd(["connect", host_port], timeout=10, use_target=False)
        output = (stdout + stderr).strip()
        if code == 0 and ("connected to" in output or "already connected" in output):
            return True, output
        return False, output or "Could not connect -- check the IP:port and that the device is reachable."

    def disconnect_wireless(self, host_port: str = "") -> tuple:
        """`adb disconnect [ip:port]`. Empty host_port disconnects all
        wireless devices."""
        args = ["disconnect"]
        if host_port:
            args.append(host_port)
        code, stdout, stderr = self.run_adb_cmd(args, timeout=8, use_target=False)
        return code == 0, (stdout + stderr).strip()
