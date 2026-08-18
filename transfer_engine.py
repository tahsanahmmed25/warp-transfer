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
    # Signals for whole-directory batch completion/failure (Phase 1 batching)
    batch_completed = pyqtSignal(object, int, int)  # BatchJob instance, file_count, total_bytes
    batch_failed = pyqtSignal(object, str)      # BatchJob instance, error_message
    # Live progress DURING a batch's single subprocess call (fix for "progress
    # stuck at 0%" -- see _process_batch docstring). Carries the BatchJob
    # identity (since up to 4 workers can have different batches in flight
    # at once) plus a rough files-so-far count for that specific batch.
    batch_progress = pyqtSignal(object, int)     # BatchJob instance, files_done_estimate

    def __init__(self, adb_manager, direction, queue, coordinator, throttle_kbps=0):
        super().__init__()
        self.adb_manager = adb_manager
        self.direction = direction  # "phone_to_pc" or "pc_to_phone"
        self.queue = queue
        self.coordinator = coordinator  # used to check paused/running state
        self.throttle_kbps = throttle_kbps
        self.running = True
        # Handle to whatever adb subprocess this worker currently has
        # in-flight, so stop() can kill it immediately instead of waiting
        # for it to finish naturally. FIX (Tahsan real-device report: "the
        # cancel button takes so much time"): previously _process_single/
        # _process_batch used the blocking subprocess.run(...), which gives
        # no handle back until the call itself returns -- setting
        # self.running = False had no way to actually interrupt an
        # in-flight adb pull/push, so Cancel had to wait out whichever
        # subprocess (up to a 60s single-file timeout, or file_count*2
        # seconds for a big batch) was already running.
        self._current_proc = None

    def run(self):
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        while self.running and not self.queue.empty():
            # Pause support: sit here without consuming the queue while the
            # coordinator is paused. Checked between files rather than
            # mid-file since adb pull/push/exec-out are already
            # subprocess-atomic per file (and batches are atomic per
            # directory-call).
            while self.coordinator.paused and self.running:
                time.sleep(0.2)
            if not self.running:
                break

            item = self.queue.get()
            try:
                if isinstance(item, BatchJob):
                    self._process_batch(item, creationflags)
                else:
                    self._process_single(item, creationflags)
            except Exception as e:
                if isinstance(item, BatchJob):
                    self.batch_failed.emit(item, str(e))
                else:
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
            self.adb_manager.run_adb_cmd(["shell", "mkdir", "-p", f"'{android_dest_dir}'"])
            cmd = [self.adb_manager.adb_path, "push", item.src, item.dest.replace("\\", "/")]

        # Popen + communicate(timeout=...) instead of subprocess.run(...) --
        # functionally equivalent, but exposes the live Popen handle via
        # self._current_proc so stop() can terminate() it immediately (see
        # Worker.__init__ / stop() docstrings).
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags
        )
        self._current_proc = proc
        try:
            stdout, stderr = proc.communicate(timeout=60)
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

    def _process_batch(self, batch: BatchJob, creationflags):
        """Pulls/pushes an entire directory in one subprocess call instead of
        one call per file inside it -- the Phase 1 speed fix. Previously,
        backing up a folder of N files meant N separate `adb.exe` spawns +
        protocol handshakes; this collapses that to one call per eligible
        top-level directory. Falls back to per-file transfer (via
        TransferCoordinator.on_batch_failed) if the batch call itself fails,
        so a single bad file doesn't silently drop the whole directory with
        no detail on which file was the problem.

        FIX ("progress isn't actually showing up" -- real-device report on a
        4324-file backup stuck at "0.0%" the whole time): this previously
        used a single blocking subprocess.run(..., timeout=...) call, which
        gives no signal of any kind until the ENTIRE directory finishes --
        for a big backup that's the whole transfer duration sitting at 0%,
        then jumping straight to done. Now uses Popen + a lightweight polling
        loop (every 0.6s) that estimates progress by counting files that
        have actually landed at the destination so far, emitting
        batch_progress so the UI has something real to show instead of a
        frozen bar. This is an ESTIMATE, not an exact byte-level count --
        adb pull/push give no structured progress output to parse -- but a
        moving, roughly-accurate count is a large improvement over total
        silence, and it converges on the real number by the time the batch
        finishes (verify_integrity() still does the authoritative check
        afterward regardless).

        The same polling loop is also what makes Cancel responsive during a
        batch now: it checks self.running every tick and terminates the
        subprocess immediately, instead of the old blocking call which
        could only be interrupted by the OS-level timeout.
        """
        try:
            if self.direction == "phone_to_pc":
                os.makedirs(batch.dest_root, exist_ok=True)
                cmd = [self.adb_manager.adb_path, "pull", batch.src_dir, batch.dest_root]
            else:  # pc_to_phone
                android_dest_root = batch.dest_root.replace("\\", "/")
                self.adb_manager.run_adb_cmd(["shell", "mkdir", "-p", f"'{android_dest_root}'"])
                cmd = [self.adb_manager.adb_path, "push", batch.src_dir, android_dest_root]

            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags
            )
            self._current_proc = proc

            poll_interval = 0.6
            last_poll = 0.0
            while proc.poll() is None:
                if not self.running:
                    proc.terminate()
                    break
                now = time.time()
                if now - last_poll >= poll_interval:
                    last_poll = now
                    counted = self._estimate_batch_progress(batch)
                    if counted is not None:
                        self.batch_progress.emit(batch, counted)
                time.sleep(0.1)

            stdout, stderr = proc.communicate()
            returncode = proc.returncode
            self._current_proc = None

            if not self.running:
                # Cancelled mid-batch -- don't treat the terminated process's
                # non-zero exit as a real error; the coordinator's own
                # self.running check in run()'s wait loop handles the actual
                # "transfer cancelled" outcome.
                return

            if returncode == 0:
                self.batch_completed.emit(batch, batch.file_count, batch.total_size)
            else:
                self.batch_failed.emit(batch, stderr or "Batch transfer failed.")
        except Exception as e:
            self._current_proc = None
            self.batch_failed.emit(batch, str(e))

    def _estimate_batch_progress(self, batch: BatchJob) -> "int | None":
        """Rough files-copied-so-far count for a batch still mid-transfer.
        phone_to_pc: counts files that have actually landed under
        batch.dest_root on local disk (cheap, no subprocess). pc_to_phone:
        asks the device via `find | wc -l` (one extra adb round-trip per
        poll tick -- acceptable at a 0.6s interval, and only runs while a
        pc_to_phone batch is actually in flight). Returns None on any error
        rather than raising -- a failed progress ESTIMATE should never take
        down the actual transfer."""
        try:
            if self.direction == "phone_to_pc":
                if not os.path.isdir(batch.dest_root):
                    return 0
                count = 0
                for _root, _dirs, files in os.walk(batch.dest_root):
                    count += len(files)
                return min(count, batch.file_count)
            else:
                android_dir = batch.dest_root.rstrip("/")
                code, stdout, _ = self.adb_manager.run_adb_cmd(
                    ["shell", f"find '{android_dir}' -type f | wc -l"], timeout=5
                )
                if code != 0:
                    return None
                return min(int((stdout or "0").strip()), batch.file_count)
        except Exception:
            return None

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
    # Overall progress updates
    # current_files, total_files, percent, speed_mbs, eta_seconds, current_file_name
    progress_updated = pyqtSignal(int, int, float, float, float, str)
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
        self.batch_fallback_log = []
        # Live in-flight batch progress estimates, keyed by id(batch) so
        # multiple concurrent batches (up to worker_count) track separately.
        # Populated by on_batch_progress(), cleared for a batch once it
        # genuinely completes (on_batch_completed) or fails (on_batch_failed)
        # -- see run()'s progress-emitting loop for how this combines with
        # self.copied_files to produce the number actually shown on screen.
        self._live_batch_estimates = {}

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

        # Snapshot which top-level source directories each item belongs to
        # BEFORE conflict resolution can remove (skip) or rename items --
        # _plan_batches() needs this to detect whether a directory's file
        # set was left fully intact (safe to batch) or altered (must fall
        # back to per-file transfer for that directory).
        original_groups = {}
        for it in items_to_transfer:
            if it.batch_key:
                original_groups.setdefault(it.batch_key, []).append(it)

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

        # 2b. Split into whole-directory batch jobs (one adb call per
        # eligible directory) and individual per-file items (Phase 1 speed
        # fix -- see _plan_batches for eligibility rules).
        batch_jobs, individual_items = self._plan_batches(items_to_transfer, original_groups)

        for job in batch_jobs:
            self.transfer_queue.put(job)
        for item in individual_items:
            self.transfer_queue.put(item)

        # 3. Determine worker count (throttled transfers stay single-stream so
        # the configured cap is meaningful instead of being ~4x'd by parallelism)
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
            w.batch_completed.connect(self.on_batch_completed)
            w.batch_failed.connect(self.on_batch_failed)
            w.batch_progress.connect(self.on_batch_progress)
            self.workers.append(w)
            w.start()

        # 5. Wait for all items to complete or cancel
        while self.running and (self.copied_files + len(self.errors)) < self.total_files:
            if not self.paused:
                estimated_files = self.copied_files + sum(self._live_batch_estimates.values())
                estimated_files = min(estimated_files, self.total_files)
                elapsed = time.time() - self.start_time
                speed = (self.copied_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0.0
                eta = self._calc_eta_seconds(speed)
                percent = (estimated_files / self.total_files * 100) if self.total_files > 0 else 0
                self.progress_updated.emit(
                    estimated_files, self.total_files, percent, speed, eta, "Transferring files..."
                )
            time.sleep(0.2)

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

    def on_batch_progress(self, batch, files_done_estimate):
        """Live progress DURING a batch's single subprocess call -- see
        Worker._process_batch. Just updates the estimate dict; run()'s own
        0.2s loop is what actually emits progress_updated using it, so this
        doesn't need to (and shouldn't -- it fires on a worker thread, and
        emitting Qt signals cross-thread on every poll tick from multiple
        possible workers is unnecessary contention when run()'s loop already
        polls at a similar cadence)."""
        self._live_batch_estimates[id(batch)] = files_done_estimate

    def on_batch_completed(self, batch, file_count, total_bytes):
        """Counterpart to on_file_completed for a whole-directory batch
        transfer -- bumps copied_files/copied_bytes by the batch's totals at
        once rather than per-file, since a batch `adb pull`/`push` gives no
        live per-file callback during the call itself (the batch_progress
        signal handles live UI feedback separately -- see on_batch_progress
        -- this is the authoritative final count once the batch is done)."""
        self._live_batch_estimates.pop(id(batch), None)
        self.copied_files += file_count
        self.copied_bytes += total_bytes

        elapsed = time.time() - self.start_time
        speed = (self.copied_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0.0
        eta = self._calc_eta_seconds(speed)
        percent = (self.copied_bytes / self.total_bytes * 100) if self.total_bytes > 0 else 0

        self.progress_updated.emit(
            self.copied_files, self.total_files, percent, speed, eta,
            f"Transferred folder ({file_count} files)"
        )

    def on_batch_failed(self, batch: BatchJob, error: str):
        """A batch directory transfer failed as a whole subprocess call --
        rather than losing the entire directory to one opaque error, fall
        back by re-queueing every file in it individually so the normal
        per-file path (with its own real error detail per failing file) can
        take over. This is genuinely a retry, not a failure log entry, so it
        deliberately does NOT append to self.errors -- see batch_fallback_log
        docstring in __init__."""
        self._live_batch_estimates.pop(id(batch), None)
        self.batch_fallback_log.append(
            f"Batch transfer failed for '{batch.src_dir}' ({batch.file_count} files), "
            f"falling back to per-file transfer. Batch error: {error}"
        )
        for item in batch.member_items:
            self.transfer_queue.put(item)

    # ---------------------------------------------------------------
    # Batch planning (Phase 1 speed fix)
    # ---------------------------------------------------------------

    def _plan_batches(self, items: list, original_groups: dict):
        """Splits the final (post-conflict-resolution) item list into
        whole-directory BatchJobs (one adb call per directory) and
        individual TransferItems, based on which top-level source
        directories are still safe to transfer as a single recursive
        `adb pull`/`push` call.

        A directory group is eligible only if BOTH:
          - every file originally scanned from it is still present in the
            final list (nothing was removed by "skip" conflict resolution --
            a batch pull/push has no way to selectively skip individual
            files, so a partial skip forces the whole group to per-file).
          - none of its items had their destination changed ("rename"
            conflict resolution -- a batch call always writes to the
            natural, un-renamed destination path).
        "overwrite" resolution doesn't disqualify a group: a fresh directory
        pull/push overwrites existing destination files by default anyway,
        matching what the per-file path already does for that mode.

        Throttled transfers never batch (see Worker._copy_throttled) -- they
        force worker_count=1 and stream chunk-by-chunk for rate limiting,
        which a single opaque `adb pull`/`push` call can't support.
        """
        if self.throttle_kbps > 0:
            return [], items

        final_groups = {}
        individuals = []
        for it in items:
            if it.batch_key:
                final_groups.setdefault(it.batch_key, []).append(it)
            else:
                individuals.append(it)

        batch_jobs = []
        for key, group_items in final_groups.items():
            original_count = len(original_groups.get(key, []))
            any_renamed = any(gi.dest_was_modified for gi in group_items)
            nothing_skipped = len(group_items) == original_count
            if nothing_skipped and not any_renamed:
                batch_jobs.append(BatchJob(key, self.dest_path, group_items))
            else:
                individuals.extend(group_items)

        return batch_jobs, individuals

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
        transfer, or None if the user cancelled. Mutates self.skipped_files.
        Renamed items get dest_was_modified=True so _plan_batches() knows
        their containing directory can no longer be safely batch-transferred."""
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
                item.dest_was_modified = True
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

                    # Defensive None guard: run_adb_cmd's subprocess call can
                    # in principle still hand back stdout=None (e.g. a
                    # process-level failure before any output was captured),
                    # and a bare `.strip()` on that crashes with
                    # AttributeError. The actual crash seen on real-device
                    # testing was a cp1252 decode failure now fixed at the
                    # source in AdbManager.run_adb_cmd (explicit utf-8 +
                    # errors='replace'), but this guard stays regardless as
                    # a safety net -- it doesn't mask genuine scan failures,
                    # since code != 0 or an empty result already falls
                    # through to the same fallback path below.
                    if code != 0 or not (stdout or "").strip():
                        # Fallback to recursively listing files if find/stat fails
                        code, stdout, stderr = self.adb_manager.run_adb_cmd(["shell", f"ls -R -l '{src}'"])
                        # Simple parsing for ls -R (basic fallback)
                        self.errors.append("Fallback scanning not fully implemented or failed.")
                        continue

                    # Only tag items with batch_key when no extension filter
                    # is active -- a batch adb pull/push can't selectively
                    # include/exclude files by extension mid-stream, so a
                    # filtered directory must stay on the per-file path.
                    batch_key = src if self.extensions is None else None

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
                                items.append(TransferItem(file_path, dest_file, size, batch_key=batch_key))
                            except ValueError:
                                continue
                else:
                    if self.extensions is not None and not self._matches_extension(src):
                        continue
                    # Single file -- never batched (batch_key stays None; a
                    # lone file isn't worth a directory-level batch call).
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
                    batch_key = src if self.extensions is None else None
                    for root, _, files in os.walk(src):
                        for file in files:
                            if self.extensions is not None and not self._matches_extension(file):
                                continue
                            full_path = os.path.join(root, file)
                            size = os.path.getsize(full_path)
                            # Relative path matching
                            rel_path = os.path.relpath(full_path, os.path.dirname(src)).replace("\\", "/")
                            dest_file = (self.dest_path.rstrip("/") + "/" + rel_path).replace("//", "/")
                            items.append(TransferItem(full_path, dest_file, size, batch_key=batch_key))
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
        """Verifies file existence and sizes match between source and destination.

        FIX (found reviewing the batch code ahead of a real Phase 1 speed
        test): the pc_to_phone branch previously issued one `adb shell stat`
        subprocess call PER FILE regardless of whether the transfer itself
        used the batch path -- for a large push (hundreds of files),
        verification alone could take as long as the batched transfer it
        was verifying, silently eating most of Phase 1's real speedup for
        pc_to_phone specifically. (phone_to_pc verification was already
        cheap -- os.path.exists/getsize are local calls, no subprocess.)
        An unbatched verification bottleneck would have made any real speed
        test result misleading regardless of how good the transfer-side
        batching itself is, so fixing this belongs with the speed-test item.

        Now groups items by their original batch_key (same top-level
        directory grouping _plan_batches uses for the transfer itself) and
        verifies ALL of them with ONE `find | xargs stat` call against
        self.dest_path -- mirroring how scan_source_items already does its
        own batched stat lookup for scanning -- instead of one subprocess
        per file. Items with no batch_key (single files, or
        extension-filtered transfers, which never get a batch_key -- see
        scan_source_items) still verify individually, since there's no
        shared directory grouping to batch by for those.
        """
    def verify_integrity(self, items: list) -> bool:
        """Verifies file existence and sizes match between source and destination."""
        if self.direction == "phone_to_pc":
            for item in items:
                if not os.path.exists(item.dest):
                    self.errors.append(f"Missing destination file on PC: {item.dest}")
                    return False
                if os.path.getsize(item.dest) != item.size:
                    self.errors.append(f"Size mismatch for {item.dest}: expected {item.size} bytes, got {os.path.getsize(item.dest)} bytes")
                    return False
            return True

        # pc_to_phone
        grouped: dict = {}
        individuals = []
        for item in items:
            if item.batch_key:
                grouped.setdefault(item.batch_key, []).append(item)
            else:
                individuals.append(item)

        actual_sizes = {}
        if grouped:
            android_dir = self.dest_path.rstrip("/")
            find_cmd = ["shell", f"find '{android_dir}' -type f -print0 | xargs -0 stat -c '%s|%n'"]
            code, stdout, _ = self.adb_manager.run_adb_cmd(find_cmd)
            if code == 0 and stdout:
                for line in stdout.splitlines():
                    if "|" in line:
                        size_str, _, path = line.partition("|")
                        try:
                            clean_path = path.strip().replace("\\", "/")
                            size_val = int(size_str)
                            actual_sizes[clean_path] = size_val
                            # Handle /sdcard <-> /storage/emulated/0 symlink parity
                            if clean_path.startswith("/storage/emulated/0/"):
                                actual_sizes["/sdcard/" + clean_path[len("/storage/emulated/0/"):].lstrip("/")] = size_val
                            elif clean_path.startswith("/sdcard/"):
                                actual_sizes["/storage/emulated/0/" + clean_path[len("/sdcard/"):].lstrip("/")] = size_val
                        except ValueError:
                            continue

            # Verify grouped items
            for group_items in grouped.values():
                for item in group_items:
                    android_dest = item.dest.replace("\\", "/")
                    size = actual_sizes.get(android_dest)
                    if size is None:
                        # Normalize path and check again
                        norm_dest = android_dest
                        if norm_dest.startswith("/sdcard/"):
                            norm_dest = "/storage/emulated/0/" + norm_dest[len("/sdcard/"):].lstrip("/")
                        elif norm_dest.startswith("/storage/emulated/0/"):
                            norm_dest = "/sdcard/" + norm_dest[len("/storage/emulated/0/"):].lstrip("/")
                        size = actual_sizes.get(norm_dest)

                    if size is None:
                        # Fallback to direct stat query before failing
                        code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"stat -c '%s' '{android_dest}'"])
                        if code == 0 and stdout:
                            try:
                                size = int(stdout.strip())
                            except ValueError:
                                size = None

                    if size != item.size:
                        self.errors.append(f"Integrity failure on phone for {android_dest}: expected {item.size} bytes, got {size}")
                        return False

        for item in individuals:
            android_dest = item.dest.replace("\\", "/")
            code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"stat -c '%s' '{android_dest}'"])
            if code != 0:
                self.errors.append(f"Missing file on phone: {android_dest}")
                return False
            try:
                android_size = int(stdout.strip())
                if android_size != item.size:
                    self.errors.append(f"Size mismatch on phone for {android_dest}: expected {item.size} bytes, got {android_size} bytes")
                    return False
            except ValueError:
                self.errors.append(f"Could not parse size for {android_dest}")
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
