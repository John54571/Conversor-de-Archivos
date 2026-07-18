import shutil
import subprocess
from pathlib import Path


def check_ffmpeg() -> bool:
    if hasattr(shutil.which, "cache_clear"):
        shutil.which.cache_clear()
    return shutil.which("ffmpeg") is not None


def check_ffmpeg_version() -> str | None:
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            first_line = result.stdout.split("\n")[0]
            return first_line.strip()
    except Exception:
        pass
    return None


def get_ffmpeg_path() -> str | None:
    if hasattr(shutil.which, "cache_clear"):
        shutil.which.cache_clear()
    return shutil.which("ffmpeg")


def check_ffprobe() -> bool:
    if hasattr(shutil.which, "cache_clear"):
        shutil.which.cache_clear()
    return shutil.which("ffprobe") is not None
