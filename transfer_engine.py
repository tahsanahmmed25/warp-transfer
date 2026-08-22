# Multithreaded Parallel Transfer Engine wrapping ADB subprocesses for Warp Transfer

import os
import posixpath
import sys
import shutil
import time
import threading
import subprocess
from queue import Queue
from PyQt6.QtCore import QThread, pyqtSignal, QObject


class TransferItem:
    def __init__(self, src, dest, size, batch_key=None):
        self.src = src      # Full source path
        self.dest = dest    # Full destination path
        self.size = size    # Size in bytes
        # If set, the top-level source directory (one of self.src_paths) this
        # item was scanned from -- only set when no extension filter is
        # active, since a directory-level `adb pull`/`push` batch can't skip
        # individual files by extension. Used by TransferCoordinator._plan_batches()
        # to decide whether this item's whole containing directory is safe to
        # transfer in a single subprocess call instead of one call per file.
        self.batch_key = batch_key
        # Flipped to True by conflict resolution if this item's destination
        # was changed (rename mode). A batch pull/push always writes to the
        # "natural" destination path, so any renamed item disqualifies its
        # whole batch group -- see _plan_batches().
        self.dest_was_modified = False


class BatchJob:
    """Represents a whole source directory queued for a single
    `adb pull`/`adb push` call instead of one subprocess per file inside it.
    Only created for directories where every contained file still ends up at
    its natural (un-renamed, non-skipped) destination -- see
    TransferCoordinator._plan_batches()."""

    def __init__(self, src_dir, dest_root, member_items):
        self.src_dir = src_dir          # top-level source directory
        self.dest_root = dest_root      # destination root adb pull/push writes into
        self.member_items = member_items  # the individual TransferItems it covers
        self.file_count = len(member_items)
        self.total_size = sum(i.size for i in member_items)


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
        self._current_proc = None

    def run(self):
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        while self.running and not self.queue.empty():
            # Pause support: sit here without consuming the queue while the coordinator is paused
            while self.coordinator.paused and self.running:
                time.sleep(0.2)
            if not self.running:
                break

            item = self.queue.get()
            try:
                self._process_single(item, creationflags)
            except Exception as e:
                self.error_occurred.emit(item.src, str(e))
            finally:
                self.queue.task_done()

    def _process_single(self, item, creationflags):
        dest_dir = os.path.dirname(item.dest)

        if self.throttle_kbps > 0:
            ok, err = self._copy_throttled(item, creationflags)
            if ok:
                self.file_completed.emit(item.src, item.size)
            else:
                self.error_occurred.emit(item.src, err)
            return

        if self.direction == "phone_to_pc":
            os.makedirs(dest_dir, exist_ok=True)
            cmd = [self.adb_manager.adb_path, "pull", item.src, item.dest]
        else:  # pc_to_phone
            android_dest_dir = dest_dir.replace("\\", "/")
            if android_dest_dir not in self.coordinator.created_remote_dirs:
                safe_android_dir = android_dest_dir.replace("'", "'\\''")
                self.adb_manager.run_adb_cmd(["shell", "mkdir", "-p", f"'{safe_android_dir}'"])
                self.coordinator.created_remote_dirs.add(android_dest_dir)
            cmd = [self.adb_manager.adb_path, "push", item.src, item.dest.replace("\\", "/")]

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags
        )
        self._current_proc = proc
        try:
            stdout, stderr = proc.communicate(timeout=180)
            returncode = proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            returncode = -1
            stderr = stderr or "Timed out."
        finally:
            self._current_proc = None

        if returncode == 0:
            self.file_completed.emit(item.src, item.size)
        else:
            self.error_occurred.emit(item.src, stderr)

    def _copy_throttled(self, item, creationflags):
        """Rate-limited copy path used when the user has set a transfer
        speed cap in Settings. adb pull/push give us no byte-level control,
        so instead we stream the file ourselves in fixed-size chunks and
        sleep between them to hold to throttle_kbps:
          - phone_to_pc: `adb exec-out cat <src>` piped to a local file.
          - pc_to_phone: local file piped into `adb shell "cat > <dest>"`.
        Slower than the native path (no compression, single-stream), which
        is the expected and accepted tradeoff for a user-requested cap.
        Never used for batches -- throttled transfers force worker_count=1
        and stay fully per-file/streamed (see TransferCoordinator._plan_batches)."""
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
        # Immediately kill whatever adb subprocess is in-flight, rather than
        # letting Cancel silently wait for it to finish on its own -- see
        # the docstring on self._current_proc in __init__.
        proc = self._current_proc
        if proc is not None and proc.poll() is None:
            try:
                proc.terminate()
            except Exception:
                pass


class TransferCoordinator(QThread):
    # Overall progress updates:
    # current_files, total_files, current_bytes, total_bytes, percent, speed_mbs, eta_seconds, current_file_name
    progress_updated = pyqtSignal(int, int, int, int, float, float, float, str)
    stage_changed = pyqtSignal(str, str)  # stage_id, stage_description ('indexing', 'setup', 'streaming', 'verifying')
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
        # Informational log of batch->per-file fallbacks (Phase 1 batching).
        # Deliberately separate from self.errors: a batch falling back to
        # per-file isn't itself a failed transfer -- the individual files get
        # re-queued and may all still succeed -- so it shouldn't count toward
        # the run()-loop's (copied_files + len(errors)) < total_files exit
        # condition the way a genuine per-file error does.
        self.created_remote_dirs = set()
        self._conflict_event = threading.Event()
        self._resolved_conflict_mode = "skip"

    def _calc_eta_seconds(self, speed_mbs, current_bytes=None) -> float:
        """Remaining time estimate in seconds, based on current rolling
        speed and bytes left to copy. Returns 0.0 when unknown."""
        if speed_mbs <= 0 or self.total_bytes <= 0:
            return 0.0
        bytes_done = self.copied_bytes if current_bytes is None else current_bytes
        remaining_bytes = max(self.total_bytes - bytes_done, 0)
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
        self.stage_changed.emit("indexing", "Scanning files and calculating sizes...")
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
        self.stage_changed.emit("setup", "Setting up transfer channels and checking conflicts...")
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

        # Queue all individual files for multi-streamed concurrent transfer
        for item in items_to_transfer:
            self.transfer_queue.put(item)

        # 3. Determine worker count (throttled transfers stay single-stream)
        if self.throttle_kbps > 0:
            worker_count = 1
        else:
            worker_count = 4 if self.total_files > 3 or self.total_bytes > 50 * 1024 * 1024 else 1

        # 4. Launch workers
        self.stage_changed.emit("streaming", "Transferring files...")
        for _ in range(worker_count):
            w = Worker(self.adb_manager, self.direction, self.transfer_queue, self, self.throttle_kbps)
            w.file_completed.connect(self.on_file_completed)
            w.error_occurred.connect(self.on_file_error)
            self.workers.append(w)
            w.start()

        # 5. Wait for all items to complete or cancel with smooth, real-time live telemetry
        while self.running and (self.copied_files + len(self.errors)) < self.total_files:
            if not self.paused:
                elapsed = max(time.time() - self.start_time, 0.001)
                speed = (self.copied_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0.0
                eta = self._calc_eta_seconds(speed, self.copied_bytes)
                
                if self.total_bytes > 0:
                    percent = (self.copied_bytes / self.total_bytes * 100)
                elif self.total_files > 0:
                    percent = (self.copied_files / self.total_files * 100)
                else:
                    percent = 0.0

                self.progress_updated.emit(
                    self.copied_files, self.total_files, self.copied_bytes, self.total_bytes,
                    percent, speed, eta, "Transferring files..."
                )
            time.sleep(0.1)

        for w in self.workers:
            w.stop()
            w.wait()

        if not self.running:
            self.transfer_finished.emit(False, "Transfer cancelled by user.")
            return

        # 6. Verification Phase
        self.stage_changed.emit("verifying", "Verifying file integrity...")
        self.emit_progress("Verifying file integrity...", 99)
        verification_passed = self.verify_integrity(items_to_transfer)

        if not verification_passed:
            err_msg = "Integrity check failed. Some files were not copied correctly. Nothing was deleted."
            if self.errors:
                err_msg = f"Integrity check failed ({len(self.errors)} issue(s)). Nothing was deleted."
            self.transfer_finished.emit(False, err_msg)
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
        self.progress_updated.emit(
            self.copied_files, self.total_files, self.copied_bytes, self.total_bytes,
            percent, 0.0, 0.0, message
        )

    def on_file_completed(self, path, size):
        self.copied_files += 1
        self.copied_bytes += size
        filename = os.path.basename(path)

        elapsed = max(time.time() - self.start_time, 0.001)
        speed = (self.copied_bytes / (1024 * 1024)) / elapsed
        eta = self._calc_eta_seconds(speed, self.copied_bytes)
        percent = (self.copied_bytes / self.total_bytes * 100) if self.total_bytes > 0 else 0

        self.progress_updated.emit(
            self.copied_files, self.total_files, self.copied_bytes, self.total_bytes,
            percent, speed, eta, f"Copying {filename}"
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
            safe_dest = item.dest.replace("'", "'\\''")
            code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"stat -c '%s' '{safe_dest}'"])
            return code == 0 and (stdout or "").strip() != ""

    def _unique_dest(self, item: TransferItem) -> str:
        """Appends ' (1)', ' (2)', ... before the extension until a
        non-colliding name is found."""
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
        return item.dest

    def _resolve_conflicts(self, items: list):
        """Resolves file conflicts based on mode."""
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
            return items

        if mode == "skip":
            conflicting_set = {id(i) for i in conflicting}
            kept = [i for i in items if id(i) not in conflicting_set]
            self.skipped_files = len(items) - len(kept)
            return kept

        if mode == "rename":
            for item in conflicting:
                item.dest = self._unique_dest(item)
                item.dest_was_modified = True
            return items

        return items

    def scan_source_items(self) -> list:
        items = []
        if self.direction == "phone_to_pc":
            for raw_src in self.src_paths:
                src = raw_src.rstrip("/\\")
                code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"[ -d '{src}' ] && echo 'dir' || echo 'file'"])
                is_dir = stdout.strip() == "dir"

                if is_dir:
                    find_cmd = ["shell", f"find '{src}' -type f -print0 | xargs -0 stat -c '%s|%n'"]
                    code, stdout, stderr = self.adb_manager.run_adb_cmd(find_cmd)

                    if code != 0 or not (stdout or "").strip():
                        code, stdout, stderr = self.adb_manager.run_adb_cmd(["shell", f"ls -R -l '{src}'"])
                        self.errors.append(f"Scanning failed for phone folder: {src}")
                        continue

                    batch_key = src if self.extensions is None else None
                    parent_dir = posixpath.dirname(src)

                    for line in stdout.splitlines():
                        if "|" in line:
                            parts = line.split("|", 1)
                            try:
                                size = int(parts[0])
                                file_path = parts[1].strip()
                                if self.extensions is not None and not self._matches_extension(file_path):
                                    continue
                                if parent_dir in ("", "/"):
                                    rel_path = file_path.lstrip("/")
                                else:
                                    rel_path = posixpath.relpath(file_path, parent_dir)
                                rel_path = rel_path.replace("/", "\\")
                                dest_file = os.path.join(self.dest_path, rel_path)
                                items.append(TransferItem(file_path, dest_file, size, batch_key=batch_key))
                            except ValueError:
                                continue
                else:
                    if self.extensions is not None and not self._matches_extension(src):
                        continue
                    code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"stat -c '%s' '{src}'"])
                    try:
                        size = int(stdout.strip())
                        dest_file = os.path.join(self.dest_path, posixpath.basename(src))
                        items.append(TransferItem(src, dest_file, size))
                    except ValueError:
                        self.errors.append(f"Could not read size of file: {src}")
        else:  # pc_to_phone
            for raw_src in self.src_paths:
                src = os.path.abspath(raw_src.rstrip("/\\"))
                posix_dest_root = self.dest_path.rstrip("/\\").replace("\\", "/")
                if os.path.isdir(src):
                    batch_key = src if self.extensions is None else None
                    src_parent = os.path.dirname(src)
                    for root, _, files in os.walk(src):
                        for file in files:
                            if self.extensions is not None and not self._matches_extension(file):
                                continue
                            full_path = os.path.join(root, file)
                            size = os.path.getsize(full_path)
                            rel_path = os.path.relpath(full_path, src_parent).replace("\\", "/")
                            dest_file = (posix_dest_root + "/" + rel_path).replace("//", "/")
                            items.append(TransferItem(full_path, dest_file, size, batch_key=batch_key))
                else:
                    if os.path.exists(src):
                        if self.extensions is not None and not self._matches_extension(src):
                            continue
                        size = os.path.getsize(src)
                        dest_file = (posix_dest_root + "/" + os.path.basename(src)).replace("//", "/")
                        items.append(TransferItem(src, dest_file, size))
        return items

    def _matches_extension(self, path: str) -> bool:
        _, dot, ext = path.rpartition(".")
        if not dot:
            return False
        return ext.lower() in self.extensions

    def verify_integrity(self, items: list) -> bool:
        """Verifies file existence and sizes match between source and destination.
        Returns True if all items transferred correctly."""
        if not items:
            return True

        failed_items = []

        if self.direction == "phone_to_pc":
            for item in items:
                dest = os.path.abspath(item.dest)
                found_path = None

                if os.path.exists(dest):
                    found_path = dest
                else:
                    # Check relative candidate directly in dest_path
                    candidate_rel = os.path.join(self.dest_path, os.path.basename(item.dest))
                    if os.path.exists(candidate_rel):
                        found_path = candidate_rel
                    else:
                        # Search dest_path recursively for the target basename
                        target_name = os.path.basename(item.dest)
                        for root, _, files in os.walk(self.dest_path):
                            if target_name in files:
                                found_path = os.path.join(root, target_name)
                                break

                if not found_path:
                    failed_items.append(f"Missing destination file on PC: {dest}")
                    continue

                actual_size = os.path.getsize(found_path)
                if actual_size != item.size and item.size != 0:
                    failed_items.append(f"Size mismatch for {found_path}: expected {item.size} bytes, got {actual_size} bytes")

        else:  # pc_to_phone
            for item in items:
                android_dest = item.dest.replace("\\", "/")
                safe_path = android_dest.replace("'", "'\\''")
                code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"stat -c '%s' '{safe_path}'"], timeout=6)

                if code != 0 or not (stdout or "").strip():
                    # Check alternative symlink path (/sdcard <-> /storage/emulated/0)
                    if safe_path.startswith("/sdcard/"):
                        alt_path = "/storage/emulated/0/" + safe_path[len("/sdcard/"):].lstrip("/")
                    elif safe_path.startswith("/storage/emulated/0/"):
                        alt_path = "/sdcard/" + safe_path[len("/storage/emulated/0/"):].lstrip("/")
                    else:
                        alt_path = safe_path
                    code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"stat -c '%s' '{alt_path}'"], timeout=6)

                if code == 0 and (stdout or "").strip():
                    try:
                        actual_size = int(stdout.strip())
                        if actual_size != item.size and item.size != 0:
                            failed_items.append(f"Size mismatch on phone for {android_dest}: expected {item.size} bytes, got {actual_size}")
                    except ValueError:
                        pass
                else:
                    failed_items.append(f"Missing file on phone: {android_dest}")

        if failed_items:
            self.errors = failed_items
            return False

        # All files verified successfully! Clear transient scan logs.
        self.errors.clear()
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
        self._resolved_conflict_mode = "cancel"
        self._conflict_event.set()
        for w in self.workers:
            w.stop()
