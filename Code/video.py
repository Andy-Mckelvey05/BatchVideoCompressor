import os
import re
import subprocess
import config


def is_video(file_name: str) -> bool:
    return (
        os.path.splitext(file_name)[1].lower()
        in config.VIDEO_EXTENSIONS
    )


def get_video_height(input_path: str):
    """
    Uses HandBrakeCLI scan output to determine source height.
    Returns height as integer, or None if detection fails.
    """

    cmd = [
        config.HANDBRAKE_PATH,
        "--scan",
        "-i",
        input_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )

        match = re.search(r"(\d{3,5})x(\d{3,5})", result.stdout)

        if match:
            width = int(match.group(1))
            height = int(match.group(2))

            print(f"📐 Detected resolution as : {width}x{height}")
            return height

    except Exception as e:
        print(f"⚠️ Could not detect resolution: {e}")

    return None