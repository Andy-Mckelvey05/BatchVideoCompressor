from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

HANDBRAKE_PATH = PROJECT_ROOT / "HandBrakeCLI.exe"

VIDEO_ENCODER = "x264"
VIDEO_QUALITY = "24"

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
}

GPU_THRESHOLD = 1.3

# None = keep original resolution
# 1080 = maximum height 1080p
# 720 = maximum height 720p
# 480 = maximum height 480p
TARGET_HEIGHT = None