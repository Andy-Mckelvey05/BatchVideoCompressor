import os
import shutil
import subprocess
import sys

# ========= CONFIG =========
HANDBRAKE_PATH = r"HandBrakeCLI.exe"

VIDEO_ENCODER = "x264"  # Uses CPU, slower but better compression
# VIDEO_ENCODER = "nvenc_h264" # Uses GPU, faster but larger files
VIDEO_QUALITY = "24"

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv"}

# ==========================

def is_video(file):
    return os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS


def compress_video(input_path, output_path):
    tmp_output = output_path + ".tmp.mp4"

    cmd = [
        HANDBRAKE_PATH,
        "-i", input_path,
        "-o", tmp_output,
        "--format", "av_mp4",
        "--optimize",
        "--markers",
        "--encoder", VIDEO_ENCODER,
        "--quality", VIDEO_QUALITY,
        "--rate", "auto",
        "--vfr",
        "--encoder-preset", "fast",
        "--encoder-profile", "auto",
        "--encoder-level", "auto",
        "--all-audio",
        "--aencoder", "copy",
        "--all-subtitles",
        "--keep-display-aspect",
    ]

    print(f"\n🎬 Compressing:\n{input_path}")

    try:
        # Launch HandBrakeCLI in a new console window
        subprocess.run(
            cmd,
            check=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except subprocess.CalledProcessError:
        print(f"❌ Failed: {input_path}")
        return

    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(tmp_output)
    if compressed_size >= original_size:
        print(f"⏭️ Compressed file larger or equal — keeping original")
        shutil.copy2(input_path, output_path)
        os.remove(tmp_output)
    else:
        os.rename(tmp_output, output_path)
        diff = original_size - compressed_size
        print(f"✅ Compression successful: {output_path} | {diff} Saved")

def process_directory(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        relative_path = os.path.relpath(root, input_dir)
        output_root = os.path.join(output_dir, relative_path)

        os.makedirs(output_root, exist_ok=True)

        for file in files:
            input_file = os.path.join(root, file)
            name, ext = os.path.splitext(file)
            output_file = os.path.join(output_root, name + ".mp4")

            if is_video(file):
                if os.path.exists(output_file):
                    print(f"⏭️ Skipping (exists): {output_file}")
                    continue
                compress_video(input_file, output_file)
            else:
                output_copy = os.path.join(output_root, file)
                if os.path.exists(output_copy):
                    print(f"⏭️ Skipping copy (exists): {output_copy}")
                    continue
                print(f"📄 Copying: {input_file}")
                shutil.copy2(input_file, output_copy)

def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("python script.py <input_directory> <output_directory>")
        return

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(input_dir):
        print("❌ Input directory does not exist")
        return

    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📂 Input:  {input_dir}")
    print(f"📁 Output: {output_dir}")
    print(f"⚙️ Encoder: {VIDEO_ENCODER} | Quality: {VIDEO_QUALITY}\n")

    process_directory(input_dir, output_dir)

    print("\n✅ Done!")

if __name__ == "__main__":
    main()