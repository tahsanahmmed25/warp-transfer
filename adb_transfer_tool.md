# Project: ADB Fast File Transfer Tool (Modern GUI)

## Goal
Build a Windows desktop app that copies, pastes, and moves files between
an Android phone and PC — significantly faster than Windows Explorer's
MTP-based copy — by using ADB (Android Debug Bridge) under the hood.
The user is non-technical: no technical options, jargon, or settings
should be exposed. Everything technical is handled automatically.

This will be published publicly on GitHub under the MIT license, so it
must work smoothly for any Android device and any user — not just power
users with USB debugging already enabled.

## Visual Polish — Top Priority
Visual quality matters more than anything else in this project. The app
must look like a premium, professionally designed product — not a
typical open-source utility. Reference-quality bar: think modern
macOS-style utilities, Raycast, or premium Windows 11 fluent-design
apps. Specific expectations:
- Consistent, deliberate design system: a defined color palette,
  spacing scale, and typography (a clean modern font like Inter or
  Segoe UI Variable — not default system font).
- Smooth micro-animations: progress bar fills smoothly (not choppy
  ticks), buttons have subtle hover/press states, panels transition
  with easing rather than snapping.
- Rounded corners, soft shadows/depth, dark-mode-first design with
  a light mode toggle.
- Empty states, loading states, and success/error states should each
  have their own polished visual treatment — not just plain text.
- Iconography should be consistent (use a single icon set throughout,
  e.g. Lucide or Phosphor icons — not mismatched emoji/clipart).
- This is the single most important quality bar for this project —
  if forced to trade off dev time between "extra feature" and
  "visual polish of existing feature," always choose polish.

## Context
- Target device for initial testing: rooted Redmi Note 7 Pro, USB
  debugging already enabled, custom HyperOS/Android 13 ROM with
  KernelSU.
- Public release target: any Android device, any user, most of whom
  will NOT have USB debugging enabled and may not know what it is.
- adb.exe (Android platform-tools) must be bundled or auto-downloaded
  on first run, so the user never has to install anything manually.

## Core Requirements

### 1. ADB wrapper layer (invisible to user)
- Detect connected device via `adb devices` automatically on launch.
- Use the real adb.exe binary via subprocess (not a reimplemented
  protocol) for reliability.

### 2. First-run device setup guide (critical for public release)
- If no authorized device is detected, show a polished, step-by-step
  onboarding flow (not a plain error message):
  1. "Enable Developer Options" — tap Build Number 7 times, with a
     simple illustration/screenshot.
  2. "Enable USB Debugging" — where to find the toggle, with a
     screenshot.
  3. "Allow this computer" — tap Allow on the phone's RSA fingerprint
     prompt when it appears.
  4. If still not detected after these steps, suggest installing the
     Google USB Driver (with a direct link) for devices that need it.
- This flow should feel like a native onboarding wizard (progress
  dots, back/next, clean illustrations) — not a wall of text.
- Note in the UI/README that some manufacturer ROMs (e.g. MIUI/HyperOS)
  have an additional "USB debugging (Security settings)" toggle;
  mention this as a troubleshooting tip.
- Once a device is successfully detected, remember this and skip
  straight to the main app on future launches.

### 3. Parallel transfer engine (fully automatic, hidden from user)
- Internally use 4 concurrent `adb pull`/`adb push` worker processes
  when transferring folders with many files, split by subfolder.
- For simple single-file or small-batch copies, a single worker is
  fine — no need to parallelize.
- Fully automatic and invisible — no sliders, no settings for this.

### 4. File operations — the ONLY manual actions exposed to the user:
- **Copy**: copy files/folders from phone → PC, or PC → phone, source
  remains untouched.
- **Paste**: standard paste-into-destination-folder behavior.
- **Move**: same as copy, but delete the source after a verified
  successful transfer (never delete source before verification passes).
- Support both directions: phone → PC and PC → phone.
- Support drag-and-drop of files/folders into the app window.

### 5. Integrity & safety (invisible safeguards)
- After every transfer, automatically verify file count + total size
  match between source and destination before reporting "Done" —
  and especially before deleting the source in a Move operation.
- If verification fails, show a clear, non-technical, well-designed
  error state ("Some files couldn't be copied — nothing was deleted
  from your phone") and never delete source files in that case.

### 6. Quick Action Shortcuts
- **Quick Media Backup**: pulls common media folders (DCIM, Pictures,
  Movies, Camera, Screenshots) to a remembered PC destination.
- **Quick Android Folder Backup**: pulls the entire `/sdcard/Android`
  folder — the main showcase for the parallel-worker speed boost.
- Both remember last-used destination (simple local `config.json`).
- Reuse the same Copy/verify/progress engine — no separate logic.

### 7. UI/UX details
- PyQt6 or `customtkinter` — whichever gives the more polished,
  native-feeling, animatable result (leaning PyQt6 for finer visual
  control given the polish priority).
- Progress bar shows real percentage, transfer speed (MB/s), ETA, and
  current file name/index (e.g. "Copying photo.jpg (243 of 1,204)").
- Big, clear action buttons: Copy, Paste, Move, Quick Media Backup,
  Quick Android Backup.
- No settings menu, no advanced options, no technical terms visible
  anywhere in the UI (no "MTP", "ADB", "workers", "threads", etc.).

## Non-goals
- No MTP handling — ADB-only.
- No raw ADB protocol reimplementation — wrap the official adb.exe.
- No technical settings, sliders, or jargon exposed in the UI.
- Windows only for now.

## Deliverables
1. Working Python app with polished PyQt6 (or customtkinter) GUI.
2. `requirements.txt` for dependencies.
3. Auto-bundled or auto-downloaded platform-tools — zero manual setup.
4. First-run onboarding wizard for enabling USB debugging.
5. Public-facing README: what it does, setup instructions, MIT license
   note, troubleshooting section (driver issues, MIUI/HyperOS extra
   toggle, etc.).
6. Brief internal dev notes (separate from public README) explaining
   the worker-pool logic and verification safeguards.