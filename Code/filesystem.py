import os
import shutil

from video import is_video
from compressor import compress_video


def count_videos(input_dir: str) -> int:
    total = 0

    for root, _, files in os.walk(input_dir):
        for file in files:
            if is_video(file):
                total += 1

    return total


def process_directory(input_dir: str, output_dir: str):
    total_videos = count_videos(input_dir)
    processed_videos = 0

    if total_videos == 0:
        print("✅ No videos found to process.")
        return

    print(f"🎯 Total videos found: {total_videos}\n")

    for root, _, files in os.walk(input_dir):
        relative_path = os.path.relpath(root, input_dir)
        output_root = os.path.join(output_dir, relative_path)
        os.makedirs(output_root, exist_ok=True)

        for file in files:
            input_file = os.path.join(root, file)

            name, _ = os.path.splitext(file)
            output_file = os.path.join(output_root, name + ".mp4")

            if is_video(file):
                processed_videos += 1
                percentage = round((processed_videos / total_videos) * 100)

                print(
                    f"\n[{processed_videos}/"
                    f"{total_videos} | "
                    f"{percentage}%] "
                    f"🎬 Processing:"
                )
                compress_video(input_file, output_file)

            else:
                output_copy = os.path.join(output_root, file)

                if os.path.exists(output_copy) and os.path.getsize(output_copy) > 0:
                    print(f"⏭️ Skipping copy: {output_copy}")
                    continue

                print(f"📄 Copying: {input_file}")
                shutil.copy2(input_file, output_copy)