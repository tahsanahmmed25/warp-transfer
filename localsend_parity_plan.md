# Warp Transfer → "Better than LocalSend" Implementation Plan

Goal: close LocalSend's real advantages (transport speed, motion/polish) while keeping
every ADB-specific advantage Warp Transfer already has that LocalSend structurally
cannot match (filtered smart backups, move-safety verification, conflict resolution,
transfer history, speed throttling, no per-file accept-prompt after first-time auth).
Doesn't need to be 100% better across the board -- just needs to not lose on speed/feel
while staying ahead on features.

Written up after a screenshot-driven bugfix session (raw HTML text in step 4, dead
Finish button, slow theme toggle -- see dev_notes.md Session N+2 for those fixes).

---

## Where Warp Transfer already wins (keep these, don't regress them)

- **Filtered smart backups** (Photos Only / Videos Only / Android folder) -- LocalSend
  has no concept of "just my DCIM folder," it's just files someone drags in.
- **Move-safety verification** (`TransferCoordinator.verify_integrity()` -- existence +
  byte-size check on every file before any `rm -rf` in `delete_source_items()`) --
  LocalSend has no delete-after-send story at all.
- **Conflict resolution** (skip/overwrite/rename/ask, via `_resolve_conflicts()` +
  `ConflictDialog`) -- LocalSend just overwrites or auto-renames, no per-transfer choice.
- **Transfer history** (`history_manager.py`) -- LocalSend has zero persistent log.
- **Speed throttling** (Settings presets -> `Worker._copy_throttled()`) -- LocalSend has
  no bandwidth cap.
- **Zero pairing dance once ADB is authorized once** -- after first-time setup, no QR
  codes, no accept-prompt per file.

---

## Phase 1 -- Transport speed (the actual bottleneck) ✅ DONE (see dev_notes.md Session N+3 -- untested on a real device)

**Problem, precisely:** `Worker.run()` (`transfer_engine.py`) calls
`subprocess.run([adb, "pull", item.src, item.dest], timeout=60)` **once per file**,
inside the per-item loop pulling from `self.queue`. For a 3,000-photo DCIM folder,
that's 3,000 fresh `adb.exe` process spawns + ADB protocol handshakes, even with 4
workers running in parallel. This is the single biggest reason it can't feel as fast
as LocalSend's persistent-stream model.

**Fix -- batch `adb pull`/`push` by directory instead of by file:**

`adb pull <remote_dir> <local_dir>` recurses and pulls an entire directory tree in
**one subprocess**, preserving structure.

1. In `scan_source_items()`, alongside the flat `TransferItem` list (still needed for
   conflict-checking, size totals, and per-file verification), identify which *source
   directories* are safe to batch -- no conflicts detected in that subtree, and no
   extension filter active (an extension-filtered folder must stay per-file since
   `adb pull` can't skip-by-extension mid-stream).
2. Add `Worker._copy_batch(src_dir, dest_dir)`: one `adb pull`/`push` call per safe
   directory instead of N calls for N files inside it.
3. **Progress-reporting tradeoff:** batched pulls know file-count/byte totals upfront
   (from the scan) but give no live per-file callback *during* the batch. Approach:
   show an indeterminate/pulsing state during a batch pull, then jump the counter by
   the batch's file count on completion. (A byte-polling alternative was considered --
   polling destination dir size every ~300ms for a more LocalSend-like live counter --
   but deferred unless the simpler approach feels insufficient after real testing.)
4. Filtered backups (Photos Only, Videos Only) and any batch containing an unresolved
   conflict stay on the existing per-file path -- purely an additive fast path for the
   common unfiltered case (Quick Media Backup / Android Folder Backup).
5. Verification (`verify_integrity()`) is unchanged -- it already checks every
   individual `TransferItem` regardless of how it was copied, so move-safety isn't
   weakened by batching.
6. Worker-count heuristic may need revisiting once batching lands ("many small files"
   vs "few big directories" want different concurrency shapes) -- not changed in this
   pass, flagged for later if real-world testing shows it matters.

---

## Phase 2 -- Motion & perceived smoothness ✅ DONE (see dev_notes.md Session N+4 -- untested on a real device)

Every hard `QStackedWidget.setCurrentIndex()`/`setCurrentWidget()` cut becomes a
transition, matching what `OnboardingWizard._fade_to_index()` already does for wizard
steps.

1. Extract `_fade_to_index` into a shared free function (new `ui_transitions.py`, or a
   `main.py` top-level helper) -- currently private to `OnboardingWizard`, needs a
   generic `(stacked_widget, new_index_or_widget)` signature usable from both.
2. Apply at every `main.py` transition point: `show_dashboard_page` <-> 
   `show_onboarding_page` (recurring, poll-driven -- needs a `_transition_in_progress`
   guard since `check_device_connection` fires every 1.5s), `show_settings_page` /
   `show_history_page` <-> dashboard via `return_to_dashboard`, and the transfer
   progress -> result page handoff in `on_transfer_finished`.
3. Theme toggle gets a cheap fade too, once Phase 3 lands (property-based, not
   full-stylesheet) -- a ~120ms opacity blend on `main_container` during the property
   swap to hide any remaining one-frame pop.
4. `QuickActionButton` hover-lift already exists and is good -- no changes needed, just
   confirm it survives whatever else changes.

---

## Phase 3 -- Theme architecture (the toggle-lag root cause) ✅ DONE (see dev_notes.md Session N+4 -- untested on a real device; ConflictDialog/DevicePickerDialog theme-tagging gap still open, see main.py's _tag_theme docstring)

`apply_theme()` currently calls `QApplication.instance().setStyleSheet(stylesheet)` --
a full-application-level repolish of every widget in the whole tree on every toggle,
plus rebuilding ~8 SVG icons from scratch. Real fix:

1. Rewrite `app_style.py`'s two separate `APP_STYLE_DARK`/`APP_STYLE_LIGHT` blocks into
   **one merged stylesheet** using `[theme="dark"]`/`[theme="light"]` attribute
   selectors (e.g. `#TitleBarButton[theme="dark"] { ... }`), loaded once at startup.
2. `toggle_theme()` becomes: set `widget.setProperty("theme", theme_str)` +
   `unpolish()`/`polish()` per widget (via `QApplication.instance().allWidgets()`),
   instead of re-parsing/re-cascading the entire stylesheet string from scratch.
3. Icons still need manual swapping regardless -- `get_svg_content()` bakes the accent
   color into the SVG string itself, so no QSS property change touches that; keep
   looping over the icon-bearing widgets (`theme_btn`, `history_btn`, etc.) same as
   today, just without the app-wide stylesheet cost around it.
4. `allWidgets()` iteration is fine at this app's current size; if it grows to
   hundreds of dynamically-created widgets (e.g. long history lists), scope the loop
   to top-level windows/dialogs only and let children inherit via normal style
   propagation.
5. Every selector in both current QSS blocks needs restructuring into the merged,
   property-gated version -- real rewrite of `app_style.py`, not a small patch. Same
   discipline as the existing dev_notes.md rule ("every new selector needs both dark
   and light rules") just reshaped into "every selector needs a `[theme=...]` variant."

---

## Phase 4 -- Onboarding friction (structural, can soften but not fully close)

LocalSend needs zero setup on shared WiFi. Warp Transfer needs USB debugging
authorization once, ever, per device -- permanent and correct tradeoff for the
filesystem-level access ADB gives that LocalSend's sandboxed app can't get. Two
softenings that don't fight this constraint:

1. **Remember authorized devices** -- once a device has connected successfully, skip
   straight to dashboard on next launch/reconnect instead of re-showing the wizard, if
   `list_all_devices()` / `check_devices()` can reliably detect "this device ID was
   seen before" (worth checking actual behavior rather than assuming ADB's own
   authorization cache covers this at the app level).
2. **Wireless-first nudge for returning users** -- `WirelessConnectDialog` already
   exists; consider defaulting new sessions to check for a previously-paired wireless
   connection before falling back to showing the USB wizard.

Optional / nice-to-have, not blocking.

---

## Phase 5 -- Feature extensions that go past LocalSend

Once Phases 1-3 are solid, these push ahead rather than just catching up. Don't start
before 1-3 are done and tested -- they build on the same scan/queue machinery Phase 1
is changing.

- **Delta/incremental backup** -- LocalSend re-sends everything every time. Extend the
  existing "skip" conflict mode into a real incremental-backup mode: only pull files
  newer than what's already at destination (mtime or size-mismatch check), turning
  "Quick Media Backup" into "sync my new photos" without re-transferring the whole
  DCIM folder each time.
- **Transfer scheduling** -- not in LocalSend at all. A "back up automatically when
  phone connects" toggle in Settings, using the existing `check_device_connection`
  poll as the trigger.
- **History -> re-run** -- `history_manager` already logs every transfer's
  direction/paths; add a "Repeat this backup" action on history rows.

---

## Suggested order & why

1. **Phase 1 (transport)** first -- biggest real-world impact, and everything else is
   cosmetic by comparison. Also the riskiest (touches core transfer correctness), so
   best done while attention budget is highest.
2. **Phase 3 (theme architecture)** before Phase 2 (motion) -- Phase 2's theme-toggle
   fade depends on Phase 3's cheaper property-swap being in place first; doing it in
   the other order means redoing the toggle animation twice.
3. **Phase 2 (motion)** last of the three -- mechanical, low-risk.
4. **Phase 4 & 5** whenever, fully decoupled from 1-3.
