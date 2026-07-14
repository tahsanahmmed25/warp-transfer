# Persistent transfer history log for Warp Transfer.
# Stored as a flat JSON array at ~/warp_transfer_history.json, capped at the
# most recent 200 entries so the file can't grow unbounded over years of use.

import os
import json
import time

HISTORY_PATH = os.path.join(os.path.expanduser("~"), "warp_transfer_history.json")
MAX_ENTRIES = 200


def _load_raw() -> list:
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def add_entry(direction: str, operation_type: str, file_count: int, total_bytes: int,
              success: bool, message: str, duration_seconds: float, device_name: str = ""):
    entries = _load_raw()
    entries.append({
        "timestamp": time.time(),
        "direction": direction,          # "phone_to_pc" | "pc_to_phone"
        "operation_type": operation_type,  # "copy" | "move"
        "file_count": file_count,
        "total_bytes": total_bytes,
        "success": success,
        "message": message,
        "duration_seconds": duration_seconds,
        "device_name": device_name,
    })
    entries = entries[-MAX_ENTRIES:]
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except Exception:
        pass


def get_entries(newest_first: bool = True) -> list:
    entries = _load_raw()
    return list(reversed(entries)) if newest_first else entries


def clear_history():
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    except Exception:
        pass


def format_bytes(n: int) -> str:
    if n >= 1024 ** 3:
        return f"{n / (1024 ** 3):.2f} GB"
    if n >= 1024 ** 2:
        return f"{n / (1024 ** 2):.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n} B"


def format_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    if seconds < 60:
        return f"{seconds}s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {secs:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes:02d}m"
