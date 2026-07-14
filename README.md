# ⚡ Warp Transfer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()
[![UI: PyQt6](https://img.shields.io/badge/UI-PyQt6-green.svg)]()

**Warp Transfer** is a premium, high-speed, **bi-directional** Android-to-PC and PC-to-Android file transfer utility. 

Designed as a modern, fluent-styled desktop application for Windows, it bypasses the sluggishness, freezing, and instability of the standard Windows Media Transfer Protocol (MTP) by utilizing Android Debug Bridge (ADB) under the hood driven by a multi-threaded parallel copy engine.

---

## ✨ Features

* **⚡ Blazing Fast Transfers (Bi-directional):** 
  * **Android to PC:** Pull entire directories or specific media categories using parallelized worker streams. Up to **20x faster** than Windows Explorer MTP when handling thousands of small files.
  * **PC to Android:** Drag & drop PC files or folders directly into the drop zone to push them straight to `/sdcard/Download` on your phone.
* **🌐 Wireless ADB Connection:** Connect wirelessly via Wi-Fi with Android 11+ Pairing Code handshakes or standard TCP/IP reconnection. No USB cables needed after pairing!
* **🔄 Advanced Conflict Resolution:** Keep your data safe with configurable collision handling: **Ask**, **Skip**, **Overwrite**, or **Auto-Rename** (appends `(1)`, `(2)`, etc.).
* **🎨 Premium Fluent UI (Dark/Light Modes):** An elegant, macOS-inspired interface built with PyQt6, featuring soft drop-shadow elevations, vector-drawn icon badges, smooth cross-fades, and a live titlebar theme switcher.
* **📱 Multi-Device Picker:** Plug in multiple phones or emulators and toggle between them dynamically via a clean pop-up picker.
* **⏱️ Speed Throttling & Filtering:** Apply speed caps (e.g. 512 KB/s, 2 MB/s, 10 MB/s) to save bandwidth or target specific categories with **Photos Only** or **Videos Only** filters.
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
