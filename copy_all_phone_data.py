# Script to perform high-speed, parallel copy from phone to PC, skipping existing files

import os
import sys
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor

ADB_PATH = r"C:\Users\Tahsan\Desktop\Project Simple\warp-transfer\bin\platform-tools\adb.exe"
PHONE_SRC_ROOT = "/storage/emulated/0"
PC_DEST_ROOT = r"G:\Redmi Note 7 Pro- 07-07-26"

def run_adb(args):
    # Dead-code note: this standalone script had its own unused
    # `startupinfo = None` local, the same class of leftover variable found
    # and removed from AdbManager.run_adb_cmd()/Worker.run() in
    # transfer_engine.py during the app's dead-code cleanup pass. This
    # script wasn't touched by that pass since it isn't part of the PyQt
    # app -- fixed here for consistency now that it's been read directly.
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NO_WINDOW
    result = subprocess.run(
        [ADB_PATH] + args,
        capture_output=True,
        creationflags=creationflags
    )
    stdout = result.stdout.decode('utf-8', errors='ignore') if result.stdout else ""
    stderr = result.stderr.decode('utf-8', errors='ignore') if result.stderr else ""
    return result.returncode, stdout, stderr

def main():
    print("Connecting to ADB and scanning phone storage...")
    
    # 1. Verify connection
    code, stdout, _ = run_adb(["devices"])
    if code != 0 or "device" not in stdout.splitlines()[1]:
        print("Error: Phone is not connected or not authorized via ADB.")
        return
        
    # 2. Scan phone files using space-safe print0 + xargs -0
    print("Scanning files on phone (space-safe, this might take a minute)...")
    find_cmd = ["shell", "find /storage/emulated/0 -type f -print0 | xargs -0 stat -c '%s|%n'"]
    # We ignore the exit code because find will exit with 1 when encountering permission-restricted system folders
    _, stdout, stderr = run_adb(find_cmd)
        
    lines = stdout.splitlines()
    print(f"Total objects found on phone: {len(lines)}")
    
    # 3. Filter missing or modified files
    transfer_queue = []
    skipped_count = 0
    skipped_bytes = 0
    total_bytes_to_copy = 0
    
    for line in lines:
        if not line.strip() or "|" not in line:
            continue
            
        parts = line.split("|", 1)
        try:
            size = int(parts[0])
            phone_path = parts[1].strip()
        except ValueError:
            continue
            
        # Get relative path from /storage/emulated/0
        if phone_path.startswith(PHONE_SRC_ROOT):
            rel_path = os.path.relpath(phone_path, PHONE_SRC_ROOT).replace("/", "\\")
        else:
            continue
            
        pc_path = os.path.join(PC_DEST_ROOT, rel_path)
        
        # Check if already exists on PC
        if os.path.exists(pc_path):
            try:
                if os.path.getsize(pc_path) == size:
                    skipped_count += 1
                    skipped_bytes += size
                    continue
            except Exception:
                pass
                
        transfer_queue.append((phone_path, pc_path, size))
        total_bytes_to_copy += size
        
    print(f"Already synchronized on PC: {skipped_count} files ({skipped_bytes / (1024*1024):.2f} MB)")
    print(f"Files to copy: {len(transfer_queue)} files ({total_bytes_to_copy / (1024*1024):.2f} MB)")
    
    if not transfer_queue:
        print("All files are already fully synchronized!")
        return
        
    # 4. Start concurrent copying
    print("\nStarting parallel transfer engine (4 threads)...")
    start_time = time.time()
    copied_files = 0
    copied_bytes = 0
    
    def copy_file(item):
        nonlocal copied_files, copied_bytes
        phone_file, pc_file, size = item
        
        # Ensure destination directory exists on PC
        os.makedirs(os.path.dirname(pc_file), exist_ok=True)
        
        # Pull the file
        code, _, stderr = run_adb(["pull", phone_file, pc_file])
        
        if code == 0:
            copied_files += 1
            copied_bytes += size
            elapsed = time.time() - start_time
            speed = (copied_bytes / (1024*1024)) / elapsed if elapsed > 0 else 0
            percent = (copied_bytes / total_bytes_to_copy) * 100
            
            # Safe print to console without emojis to avoid encoding crashes on Windows
            print(f"[{percent:6.2f}%] Pulled: {os.path.basename(pc_file)} ({size/1024:.1f} KB) | Speed: {speed:.2f} MB/s | {copied_files}/{len(transfer_queue)} files", flush=True)
        else:
            print(f"Failed pulling {phone_file}: {stderr}", flush=True)

    # Run in thread pool
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(copy_file, transfer_queue)
        
    elapsed_total = time.time() - start_time
    print(f"\nTransfer complete!")
    print(f"Time elapsed: {elapsed_total/60:.2f} minutes")
    print(f"Copied: {copied_files} files ({copied_bytes / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()
