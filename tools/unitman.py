from math import floor

"""
Unit conversion utilities for video compression calculations:

- kB: kilobyte
- MB: megabyte
- kbit: kilobit
- kbps: kilobit per second

NOTE: All conversions are based on base 2 (1 kB = 1024 bytes, 1 MB = 1024 kB, etc.)
"""

def B_to_kB(B: int):
    """Converts bytes to kilobytes (1024 bytes = 1 kB)."""
    return B // 1024

def kB_to_MB(kB: int):
    """Converts kilobytes to megabytes (1024 kB = 1 MB)."""
    return kB // 1024

def B_to_MB(B: int):
    """Converts bytes to megabytes."""
    return kB_to_MB(B_to_kB(B))

def MB_to_kbit(MB: int):
    """Converts megabytes to kilobits (1 MB = 8192 kbit)."""
    return MB * 8192

def kbit_to_kbps(kbits: int, sec: int):
    """Converts kilobits to kilobits per second given duration in seconds."""
    return kbits // sec

def MB_to_kbps(MB: int, sec: int):
    """Converts megabytes to kilobits per second given duration in seconds."""
    return kbit_to_kbps(MB_to_kbit(MB), sec)

def calculate_target_bitrate(target_size_mb: int, duration_s: int, overhead_p: float, audio_kbps: int):
    """Calculates target bitrates for video and overall file based on target size, duration, overhead percentage and audio bitrate."""
    target_kbits = MB_to_kbit(floor(target_size_mb * (1 - overhead_p)))
    target_kbps = kbit_to_kbps(target_kbits, duration_s)
    target_v_kbps = target_kbps - audio_kbps
    return target_v_kbps, target_kbps
