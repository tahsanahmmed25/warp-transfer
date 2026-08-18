<h1 align="center">⚡ Warp Transfer</h1>

<p align="center">
  <b>A premium, high-speed, bi-directional Android-to-PC and PC-to-Android file transfer utility bypassing MTP via ADB.</b>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python: 3.10+"></a>
  <img src="https://img.shields.io/badge/Version-1.1.0--stable-blue.svg" alt="Version: 1.1.0-stable">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform: Windows">
  <img src="https://img.shields.io/badge/UI-PyQt6-green.svg" alt="UI: PyQt6">
</p>

Designed as a modern, fluent-styled desktop application for Windows, Warp Transfer bypasses the sluggishness, freezing, and instability of the standard Windows Media Transfer Protocol (MTP) by utilizing Android Debug Bridge (ADB) under the hood driven by a multi-threaded parallel copy engine.

---

## ✨ Features

* **⚡ Blazing Fast Transfers (Bi-directional):** 
  * **Top Direction Switcher:** Effortlessly toggle between **`💻 PC ➔ 📱 Phone`** and **`📱 Phone ➔ 💻 PC`** with an instant direction swap button (`⇄`).
  * **Two-Column Split Workspace:** Interactive source file staging on the left with drag-and-drop ingestion, click-to-browse, unlimited batch file additions, individual item removals, and live storage summary.
  * **Dedicated Landing Directory & Quick Chips:** Choose arbitrary destination paths via native dialogs or jump directly to quick-pick locations (`Downloads`, `DCIM / Camera`, `Pictures`, `Movies`, `Music`, `Desktop`, `Videos`, `Warp Backup`).
* **🚀 4-Stage Transfer Stepper Pipeline:** Eliminates UI freeze perception with live stepper milestones (**Indexing ➔ Channel Setup ➔ Transferring / Streaming ➔ Verification**) complete with real-time speed tracking (`MB/s`), countdown ETA, and active file tickers.
* **🌐 Wireless ADB Connection:** Connect wirelessly via Wi-Fi with Android 11+ Pairing Code handshakes or standard TCP/IP reconnection. No USB cables needed after pairing!
* **🔄 Advanced Conflict Resolution:** Keep your data safe with configurable collision handling: **Ask**, **Skip**, **Overwrite**, or **Auto-Rename** (appends `(1)`, `(2)`, etc.).
* **🎨 Premium Fluent UI (Dark/Light Modes):** An elegant interface built with PyQt6, featuring soft drop-shadow elevations, vector-drawn icon badges, smooth cross-fades, and a live titlebar theme switcher.
* **📋 Copy vs. ✂️ Move Operations:** Non-destructive copy mode or move mode with built-in safety warnings and verification before post-move cleanup.
* **📱 Multi-Device Picker:** Plug in multiple phones or emulators and toggle between them dynamically via a clean pop-up picker.
* **⏱️ Speed Throttling:** Apply speed caps (e.g. 512 KB/s, 2 MB/s, 10 MB/s) to save bandwidth.
* **📜 Transfer History Log:** Review detailed records of past transfers, including file counts, operations, size, duration, and timestamps.
* **📦 Auto-setup Platform-Tools:** Automatically detects, downloads, and configures Android platform tools (`adb.exe`) on its first launch. No manual command-line downloads or environment PATH variables required.
* **🛡️ Integrity Safeguards:** Verifies all file existence and byte sizes before confirming completions, ensuring that source files are never deleted on a "Move" operation unless the destination is 100% verified.

---

## 🚀 Getting Started

### 📋 Prerequisites
* **Windows 10 / 11**
* **Python 3.10+** (if running from source)

### 💻 Run from Source
1. Clone this repository.
2. Navigate to the project directory and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## 🛡️ Trust & Security

Because Warp Transfer bundles and executes the official Android Debug Bridge (`adb.exe`) to communicate with your phone via USB/Wi-Fi, **Windows Defender or other antivirus products may occasionally flag the application as a false positive.**

* **Why?** Antivirus software often flags tools that interact with external USB devices or spawn background CLI sub-processes (`adb.exe` is a developer tool that has full command control over connected Android devices).
* **Our Promise:** Warp Transfer is 100% open-source under the MIT License. We do not collect, send, or modify any user data. The code runs completely locally.

---

## 🛠️ Troubleshooting

### 1. Device Not Detected
* **Enable File Transfer Mode:** When you connect your phone to the PC, make sure the USB mode on your phone's notification shade is set to **File Transfer (MTP)**, not "Charge Only".
* **Xiaomi/Redmi Devices (MIUI/HyperOS):** You must enable both **USB Debugging** and **USB Debugging (Security Settings)** in your Developer Options. The security setting is required by MIUI to allow simulating file transfers.
* **USB Driver Needed:** If your PC doesn't show the RSA fingerprint confirmation, you might need to install Google's OEM USB drivers. Click **Download USB Drivers** on the troubleshooting slide of our wizard.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](file:///C:/Users/Tahsan/Desktop/Project%20Simple/warp-transfer/LICENSE) file for details.
