import os
import shutil

import config
from encoder import encode_cpu, encode_gpu
from video import get_video_height


def get_resize_args(height: int) -> list:
    if config.TARGET_HEIGHT is None:
        return []

    if height > config.TARGET_HEIGHT:
        return [
            "--maxHeight",
            str(config.TARGET_HEIGHT),
            "--keep-display-aspect",
            "--non-anamorphic",
        ]

    print("📏 Resolution already within target | Keeping size")
    return []


def compress_video(input_path: str, output_path: str):
    print(f"\n🎬 Processing:\n{input_path}")

    height = get_video_height(input_path)

    if height is None:
        print("⚠️ Could not determine resolution.")
        print("⚡ Running normal GPU test...")
        return gpu_test_compression(input_path, output_path,[])

    resize_args = get_resize_args(height)

    # =====================================================
    # SOURCE IS ABOVE TARGET
    #
    # We know we're reducing resolution, so skip GPU test.
    # =====================================================

    if config.TARGET_HEIGHT is not None and height > config.TARGET_HEIGHT:
        print(f"📉 Source is {height}p, Downscaling to {config.TARGET_HEIGHT}p, ")
        print("🔥 Running CPU encode directly...")

        if encode_cpu(input_path, output_path, resize_args):
            print("✅ CPU encode complete")
        else:
            print("❌ CPU encode failed, | falling back to original")
            shutil.copy2(input_path, output_path,)

        return None

    # =====================================================
    # SOURCE IS ALREADY AT OR BELOW TARGET
    #
    # GPU test remains appropriate.
    # =====================================================

    gpu_test_compression(input_path, output_path, resize_args)
    return None


def gpu_test_compression(input_path: str, output_path: str, resize_args: list):
    gpu_tmp = output_path + ".gpu.mp4"

    print("⚡ Running GPU test encode...")

    if not encode_gpu(input_path, gpu_tmp, resize_args):
        print("❌ GPU encode failed | falling back to copy")
        shutil.copy2(input_path, output_path)
        return

    original_size = os.path.getsize(input_path)
    gpu_size = os.path.getsize(gpu_tmp)
    gpu_ratio = (gpu_size / original_size)

    print(f"📊 GPU size ratio: {gpu_ratio:.2f}x")

    if gpu_ratio > config.GPU_THRESHOLD:
        print("⏭️ GPU result is too large — Copying original")

        os.remove(gpu_tmp)
        shutil.copy2(input_path, output_path)

        return

    print("✅ GPU shows potential savings → running CPU encode...")
    os.remove(gpu_tmp)

    if encode_cpu(input_path, output_path, resize_args):
        print("✅ CPU encode complete.")
    else:
        print("❌ CPU encode failed | Falling back to original")
        shutil.copy2(input_path, output_path)