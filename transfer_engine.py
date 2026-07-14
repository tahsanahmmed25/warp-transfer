# Multithreaded Parallel Transfer Engine wrapping ADB subprocesses for Warp Transfer

import os
import sys
import shutil
import time
import threading
import subprocess
from queue import Queue
from PyQt6.QtCore import QThread, pyqtSignal, QObject


class TransferItem:
    def __init__(self, src, dest, size):
        self.src = src      # Full source path
        self.dest = dest    # Full destination path
        self.size = size    # Size in bytes


class Worker(QThread):
    # Signals for individual file completion
    file_completed = pyqtSignal(str, int)  # file_path, bytes_copied
    error_occurred = pyqtSignal(str, str)  # file_path, error_message

    def __init__(self, adb_manager, direction, queue, coordinator, throttle_kbps=0):
        super().__init__()
        self.adb_manager = adb_manager
        self.direction = direction  # "phone_to_pc" or "pc_to_phone"
        self.queue = queue
        self.coordinator = coordinator  # used to check paused/running state
        self.throttle_kbps = throttle_kbps
        self.running = True

    def run(self):
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        while self.running and not self.queue.empty():
            # Pause support: sit here without consuming the queue while the
            # coordinator is paused. Checked between files rather than
            # mid-file since adb pull/push/exec-out are already
            # subprocess-atomic per file.
            while self.coordinator.paused and self.running:
                time.sleep(0.2)
            if not self.running:
                break

            item = self.queue.get()
            try:
                dest_dir = os.path.dirname(item.dest)

                if self.throttle_kbps > 0:
                    ok, err = self._copy_throttled(item, creationflags)
                    if ok:
                        self.file_completed.emit(item.src, item.size)
                    else:
                        self.error_occurred.emit(item.src, err)
                else:
                    if self.direction == "phone_to_pc":
                        os.makedirs(dest_dir, exist_ok=True)
                        cmd = [self.adb_manager.adb_path, "pull", item.src, item.dest]
                    else:  # pc_to_phone
                        android_dest_dir = dest_dir.replace("\\", "/")
                        self.adb_manager.run_adb_cmd(["shell", "mkdir", "-p", f"'{android_dest_dir}'"])
                        cmd = [self.adb_manager.adb_path, "push", item.src, item.dest.replace("\\", "/")]

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        creationflags=creationflags,
                        timeout=60
                    )

                    if result.returncode == 0:
                        self.file_completed.emit(item.src, item.size)
                    else:
                        self.error_occurred.emit(item.src, result.stderr)
            except Exception as e:
                self.error_occurred.emit(item.src, str(e))
            finally:
                self.queue.task_done()

    def _copy_throttled(self, item, creationflags):
        """Rate-limited copy path used when the user has set a transfer
        speed cap in Settings. adb pull/push give us no byte-level control,
        so instead we stream the file ourselves in fixed-size chunks and
        sleep between them to hold to throttle_kbps:
          - phone_to_pc: `adb exec-out cat <src>` piped to a local file.
          - pc_to_phone: local file piped into `adb shell "cat > <dest>"`.
        Slower than the native path (no compression, single-stream), which
        is the expected and accepted tradeoff for a user-requested cap."""
        chunk_size = 64 * 1024
        bytes_per_sec = max(self.throttle_kbps * 1024, 1)
        target_seconds_per_chunk = chunk_size / bytes_per_sec

        try:
            if self.direction == "phone_to_pc":
                dest_dir = os.path.dirname(item.dest)
                os.makedirs(dest_dir, exist_ok=True)
                proc = subprocess.Popen(
                    [self.adb_manager.adb_path, "exec-out", "cat", item.src],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=creationflags
                )
                with open(item.dest, "wb") as f:
                    while True:
                        t0 = time.time()
                        chunk = proc.stdout.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        elapsed = time.time() - t0
                        remaining = target_seconds_per_chunk - elapsed
                        if remaining > 0:
                            time.sleep(remaining)
                proc.wait(timeout=120)
                if proc.returncode != 0:
                    err = proc.stderr.read().decode("utf-8", errors="ignore")
                    return False, err or "exec-out cat failed."
                return True, ""
            else:  # pc_to_phone
                dest_dir = os.path.dirname(item.dest).replace("\\", "/")
                self.adb_manager.run_adb_cmd(["shell", "mkdir", "-p", f"'{dest_dir}'"])
                android_dest = item.dest.replace("\\", "/")
                proc = subprocess.Popen(
                    [self.adb_manager.adb_path, "shell", f"cat > '{android_dest}'"],
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=creationflags
                )
                with open(item.src, "rb") as f:
                    while True:
                        t0 = time.time()
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        proc.stdin.write(chunk)
                        elapsed = time.time() - t0
                        remaining = target_seconds_per_chunk - elapsed
                        if remaining > 0:
                            time.sleep(remaining)
                proc.stdin.close()
                proc.wait(timeout=120)
                if proc.returncode != 0:
                    err = proc.stderr.read().decode("utf-8", errors="ignore")
                    return False, err or "shell cat> push failed."
                return True, ""
        except Exception as e:
            return False, str(e)

    def stop(self):
        self.running = False


class TransferCoordinator(QThread):
    # Overall progress updates
    # current_files, total_files, percent, speed_mbs, eta_seconds, current_file_name
    progress_updated = pyqtSignal(int, int, float, float, float, str)
    transfer_finished = pyqtSignal(bool, str)  # success, message
    paused_changed = pyqtSignal(bool)
    # Emitted once, pre-transfer, when conflict_mode == "ask" and one or more
    # destination files already exist. Carries the conflict count; the main
    # thread must call resolve_conflict(mode) in response or the coordinator
    # blocks indefinitely.
    conflicts_found = pyqtSignal(int)

    def __init__(self, adb_manager, direction, operation_type, src_paths, dest_path,
                 conflict_mode="ask", throttle_kbps=0, extensions=None):
        """
        direction: 'phone_to_pc' or 'pc_to_phone'
        operation_type: 'copy' or 'move'
        src_paths: list of paths to copy/move
        dest_path: destination directory path
        conflict_mode: 'ask' | 'skip' | 'overwrite' | 'rename'
        throttle_kbps: 0 = unlimited, otherwise a rate cap in KB/s
        extensions: optional list of lowercase extensions (no dot) to
                    restrict the transfer to, e.g. ['jpg', 'png']. None/[]
                    means no filtering.
        """
        super().__init__()
        self.adb_manager = adb_manager
        self.direction = direction
        self.operation_type = operation_type
        self.src_paths = src_paths
        self.dest_path = dest_path
        self.conflict_mode = conflict_mode
        self.throttle_kbps = throttle_kbps
        self.extensions = set(e.lower().lstrip(".") for e in extensions) if extensions else None

        self.total_files = 0
        self.total_bytes = 0
        self.copied_files = 0
        self.copied_bytes = 0
        self.skipped_files = 0
        self.start_time = 0

        self.transfer_queue = Queue()
        self.workers = []
        self.running = True
        self.paused = False
        self.errors = []

        self._conflict_event = threading.Event()
        self._resolved_conflict_mode = "skip"

    def _calc_eta_seconds(self, speed_mbs) -> float:
        """Remaining time estimate in seconds, based on current rolling
        speed and bytes left to copy. Returns 0.0 when unknown (no speed
        yet, or nothing left)."""
        if speed_mbs <= 0 or self.total_bytes <= 0:
            return 0.0
        remaining_bytes = max(self.total_bytes - self.copied_bytes, 0)
        remaining_mb = remaining_bytes / (1024 * 1024)
        return remaining_mb / speed_mbs

    def pause(self):
        self.paused = True
        self.paused_changed.emit(True)

    def resume(self):
        self.paused = False
        self.paused_changed.emit(False)

    def resolve_conflict(self, mode: str):
        """Called from the main thread (in response to conflicts_found) once
        the user picks skip/overwrite/rename/cancel in the conflict dialog."""
        self._resolved_conflict_mode = mode
        self._conflict_event.set()

    def run(self):
        self.running = True
        self.start_time = time.time()
        self.emit_progress("Scanning files...", 0)

        # 1. Scan files to transfer (extension filter applied inline)
        items_to_transfer = self.scan_source_items()
        if not items_to_transfer:
            if self.errors:
                self.transfer_finished.emit(False, f"Scan failed: {self.errors[0]}")
            else:
                self.transfer_finished.emit(False, "No files found to transfer.")
            return

        # 2. Conflict detection & resolution
        items_to_transfer = self._resolve_conflicts(items_to_transfer)
        if items_to_transfer is None:
            # User cancelled from the conflict dialog.
            self.transfer_finished.emit(False, "Transfer cancelled due to file conflicts.")
            return
        if not items_to_transfer:
            self.transfer_finished.emit(
                True, f"Nothing to transfer -- all {self.skipped_files} file(s) already existed and were skipped."
            )
            return

        self.total_files = len(items_to_transfer)
        self.total_bytes = sum(item.size for item in items_to_transfer)

        for item in items_to_transfer:
            self.transfer_queue.put(item)

        # 3. Determine worker count (throttled transfers stay single-stream so
        # the configured cap is meaningful instead of being ~4x'd by parallelism)
        if self.throttle_kbps > 0:
            worker_count = 1
        else:
            worker_count = 4 if self.total_files > 3 or self.total_bytes > 50 * 1024 * 1024 else 1

        # 4. Launch workers
        for _ in range(worker_count):
            w = Worker(self.adb_manager, self.direction, self.transfer_queue, self, self.throttle_kbps)
            w.file_completed.connect(self.on_file_completed)
            w.error_occurred.connect(self.on_file_error)
            self.workers.append(w)
            w.start()

        # 5. Wait for all items to complete or cancel
        # NOTE: queue.Queue.all_tasks_done is a threading.Condition object,
        # not a boolean flag. "not self.transfer_queue.all_tasks_done" is
        # ALWAYS False (Condition objects are truthy by default, having no
        # __bool__/__len__ override) -- this made the loop below exit
        # immediately after the workers were started, which then called
        # w.stop() on every worker before they'd meaningfully processed the
        # queue, breaking real transfers. Track completion using the
        # processed-item count instead, which is consistent with how
        # progress/speed is already computed from copied_bytes elsewhere.
        while self.running and (self.copied_files + len(self.errors)) < self.total_files:
            if not self.paused:
                elapsed = time.time() - self.start_time
                speed = (self.copied_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0.0
                eta = self._calc_eta_seconds(speed)
                percent = (self.copied_bytes / self.total_bytes * 100) if self.total_bytes > 0 else 0
                self.progress_updated.emit(
                    self.copied_files, self.total_files, percent, speed, eta, "Transferring files..."
                )
            time.sleep(0.2)

        for w in self.workers:
            w.stop()
            w.wait()

        if not self.running:
            self.transfer_finished.emit(False, "Transfer cancelled by user.")
            return

        # 6. Verification Phase
        self.emit_progress("Verifying file integrity...", 99)
        verification_passed = self.verify_integrity(items_to_transfer)

        if not verification_passed:
            self.transfer_finished.emit(False, "Integrity check failed. Some files were not copied correctly. Nothing was deleted.")
            return

        # 7. Post-verification cleanup (for Move operations)
        if self.operation_type == "move":
            self.emit_progress("Cleaning up source files...", 99)
            cleanup_success = self.delete_source_items()
            if not cleanup_success:
                self.transfer_finished.emit(True, "Transfer succeeded, but some source files could not be removed.")
                return

        skip_note = f" ({self.skipped_files} already-existing file(s) skipped.)" if self.skipped_files else ""
        self.transfer_finished.emit(True, f"Transfer completed and verified successfully!{skip_note}")

    def emit_progress(self, message, percent):
        self.progress_updated.emit(self.copied_files, self.total_files, percent, 0.0, 0.0, message)

    def on_file_completed(self, path, size):
        self.copied_files += 1
        self.copied_bytes += size
        filename = os.path.basename(path)

        elapsed = time.time() - self.start_time
        speed = (self.copied_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0.0
        eta = self._calc_eta_seconds(speed)
        percent = (self.copied_bytes / self.total_bytes * 100) if self.total_bytes > 0 else 0

        self.progress_updated.emit(
            self.copied_files, self.total_files, percent, speed, eta, f"Copying {filename}"
        )

    def on_file_error(self, path, error):
        self.errors.append(f"{path}: {error}")

    # ---------------------------------------------------------------
    # Conflict resolution
    # ---------------------------------------------------------------

    def _dest_exists(self, item: TransferItem) -> bool:
        if self.direction == "phone_to_pc":
            return os.path.exists(item.dest)
        else:
            code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"stat -c '%s' '{item.dest}'"])
            return code == 0 and stdout.strip() != ""

    def _unique_dest(self, item: TransferItem) -> str:
        """Appends ' (1)', ' (2)', ... before the extension until a
        non-colliding name is found, for either local or Android paths."""
        is_local = self.direction == "phone_to_pc"
        sep = "\\" if is_local else "/"
        directory = item.dest.rsplit(sep, 1)[0] if sep in item.dest else ""
        filename = item.dest.rsplit(sep, 1)[-1]
        stem, dot, ext = filename.rpartition(".")
        if not dot:
            stem, ext = filename, ""

        for n in range(1, 500):
            candidate_name = f"{stem} ({n}){('.' + ext) if ext else ''}"
            candidate = f"{directory}{sep}{candidate_name}" if directory else candidate_name
            probe = TransferItem(item.src, candidate, item.size)
            if not self._dest_exists(probe):
                return candidate
        return item.dest  # give up gracefully; falls back to overwrite behavior

    def _resolve_conflicts(self, items: list):
        """Returns the (possibly filtered/renamed) item list to actually
        transfer, or None if the user cancelled. Mutates self.skipped_files."""
        conflicting = [item for item in items if self._dest_exists(item)]
        if not conflicting:
            return items

        mode = self.conflict_mode
        if mode == "ask":
            self.conflicts_found.emit(len(conflicting))
            self._conflict_event.clear()
            self._conflict_event.wait()
            mode = self._resolved_conflict_mode
            if mode == "cancel":
                return None

        if mode == "overwrite":
            return items  # adb pull/push overwrite destination files by default

        if mode == "skip":
            conflicting_set = {id(i) for i in conflicting}
            kept = [i for i in items if id(i) not in conflicting_set]
            self.skipped_files = len(items) - len(kept)
            return kept

        if mode == "rename":
            for item in conflicting:
                item.dest = self._unique_dest(item)
            return items

        return items

    def scan_source_items(self) -> list:
        items = []
        if self.direction == "phone_to_pc":
            for src in self.src_paths:
                # Check if directory or file
                code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"[ -d '{src}' ] && echo 'dir' || echo 'file'"])
                is_dir = stdout.strip() == "dir"

                if is_dir:
                    # Find all files in the directory with sizes (space-safe)
                    # Format: size|filepath
                    find_cmd = ["shell", f"find '{src}' -type f -print0 | xargs -0 stat -c '%s|%n'"]
                    code, stdout, stderr = self.adb_manager.run_adb_cmd(find_cmd)

                    if code != 0 or not stdout.strip():
                        # Fallback to recursively listing files if find/stat fails
                        code, stdout, stderr = self.adb_manager.run_adb_cmd(["shell", f"ls -R -l '{src}'"])
                        # Simple parsing for ls -R (basic fallback)
                        self.errors.append("Fallback scanning not fully implemented or failed.")
                        continue

                    for line in stdout.splitlines():
                        if "|" in line:
                            parts = line.split("|", 1)
                            try:
                                size = int(parts[0])
                                file_path = parts[1].strip()
                                if self.extensions is not None and not self._matches_extension(file_path):
                                    continue
                                # Calculate relative path
                                rel_path = os.path.relpath(file_path, os.path.dirname(src)).replace("/", "\\")
                                dest_file = os.path.join(self.dest_path, rel_path)
                                items.append(TransferItem(file_path, dest_file, size))
                            except ValueError:
                                continue
                else:
                    if self.extensions is not None and not self._matches_extension(src):
                        continue
                    # Single file
                    code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"stat -c '%s' '{src}'"])
                    try:
                        size = int(stdout.strip())
                        dest_file = os.path.join(self.dest_path, os.path.basename(src))
                        items.append(TransferItem(src, dest_file, size))
                    except ValueError:
                        self.errors.append(f"Could not read size of file: {src}")
        else:  # pc_to_phone
            for src in self.src_paths:
                if os.path.isdir(src):
                    for root, _, files in os.walk(src):
                        for file in files:
                            if self.extensions is not None and not self._matches_extension(file):
                                continue
                            full_path = os.path.join(root, file)
                            size = os.path.getsize(full_path)
                            # Relative path matching
                            rel_path = os.path.relpath(full_path, os.path.dirname(src)).replace("\\", "/")
                            dest_file = (self.dest_path.rstrip("/") + "/" + rel_path).replace("//", "/")
                            items.append(TransferItem(full_path, dest_file, size))
                else:
                    if os.path.exists(src):
                        if self.extensions is not None and not self._matches_extension(src):
                            continue
                        size = os.path.getsize(src)
                        dest_file = (self.dest_path.rstrip("/") + "/" + os.path.basename(src)).replace("//", "/")
                        items.append(TransferItem(src, dest_file, size))
        return items

    def _matches_extension(self, path: str) -> bool:
        _, dot, ext = path.rpartition(".")
        if not dot:
            return False
        return ext.lower() in self.extensions

    def verify_integrity(self, items: list) -> bool:
        """Verifies file existence and sizes match between source and destination."""
        if self.direction == "phone_to_pc":
            for item in items:
                if not os.path.exists(item.dest):
                    return False
                if os.path.getsize(item.dest) != item.size:
                    return False
        else:  # pc_to_phone
            for item in items:
                # Query file size on Android
                code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"stat -c '%s' '{item.dest}'"])
                if code != 0:
                    return False
                try:
                    android_size = int(stdout.strip())
                    if android_size != item.size:
                        return False
                except ValueError:
                    return False
        return True

    def delete_source_items(self) -> bool:
        """Deletes original source files after successful transfer validation."""
        if self.direction == "phone_to_pc":
            for path in self.src_paths:
                code, _, _ = self.adb_manager.run_adb_cmd(["shell", "rm", "-rf", f"'{path}'"])
                if code != 0:
                    return False
        else:  # pc_to_phone
            for path in self.src_paths:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception:
                    return False
        return True

    def cancel(self):
        self.running = False
        self.paused = False
        # Unblock a conflict-dialog wait if the user cancels mid-prompt.
        self._resolved_conflict_mode = "cancel"
        self._conflict_event.set()
        for w in self.workers:
            w.stop()
