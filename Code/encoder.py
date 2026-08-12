import os
import subprocess
import config


def encode_gpu(input_path: str, output_path: str, resize_args: list) -> bool:
    cmd = [
        config.HANDBRAKE_PATH,
        "-i",
        input_path,
        "-o",
        output_path,
        *resize_args,

        "--format",
        "av_mp4",

        "--encoder",
        "nvenc_h264",

        "--quality",
        config.VIDEO_QUALITY,

        "--rate",
        "auto",

        "--vfr",

        "--all-audio",
        "--aencoder",
        "copy",

        "--all-subtitles",
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            creationflags=getattr(
                subprocess,
                "CREATE_NEW_CONSOLE",
                0,
            ),
        )

        return os.path.exists(output_path)

    except subprocess.CalledProcessError as e:
        print(f"❌ GPU encode failed: {e}")
        return False


def encode_cpu(input_path: str, output_path: str, resize_args: list) -> bool:
    cmd = [
        config.HANDBRAKE_PATH,
        "-i",
        input_path,
        "-o",
        output_path,
        *resize_args,

        "--format",
        "av_mp4",

        "--optimize",
        "--markers",

        "--encoder",
        "x264",

        "--quality",
        config.VIDEO_QUALITY,

        "--rate",
        "auto",

        "--vfr",

        "--encoder-preset",
        "fast",

        "--all-audio",
        "--aencoder",
        "copy",

        "--all-subtitles",
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            creationflags=getattr(
                subprocess,
                "CREATE_NEW_CONSOLE",
                0,
            ),
        )

        return os.path.exists(output_path)

    except subprocess.CalledProcessError as e:
        print(f"❌ CPU encode failed: {e}")
        return False