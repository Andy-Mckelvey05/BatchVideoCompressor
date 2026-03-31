import os
import shutil
import subprocess

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
        creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        subprocess.run(
            cmd,
            check=True,
            creationflags=creation_flags
        )
    except subprocess.CalledProcessError:
        print(f"❌ Failed: {input_path}")
        return

    try:
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(tmp_output)

        if compressed_size >= original_size:
            print(f"⏭️ Compressed file larger or equal — keeping original")
            shutil.copy2(input_path, output_path)
            os.remove(tmp_output)
        else:
            os.replace(tmp_output, output_path)  # safer than rename
            diff = original_size - compressed_size
            print(f"✅ Compression successful: {output_path} | {diff} Saved")

    except Exception as e:
        print(f"❌ File handling error: {e}")
        if os.path.exists(tmp_output):
            os.remove(tmp_output)

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
                if os.path.exists(output_copy) and os.path.getsize(output_copy) > 0:
                    print(f"⏭️ Skipping copy (exists): {output_copy}")
                    continue
                print(f"📄 Copying: {input_file}")
                shutil.copy2(input_file, output_copy)

def get_downloads_folder():
    return os.path.join(os.path.expanduser("~"), "Downloads")

def main():
    if shutil.which(HANDBRAKE_PATH) is None and not os.path.isfile(HANDBRAKE_PATH):
        print("❌ HandBrakeCLI not found. Make sure it's installed or the path is correct.")
        return

    print("📥 Video Compression Tool\n")

    # Get input directory
    while True:
        input_dir = input("📂 Enter input directory: ").strip()
        if os.path.exists(input_dir):
            break
        print("❌ Input directory does not exist, try again.\n")

    # Get output directory (optional)
    output_dir = input("📁 Enter output directory (leave blank for Downloads): ").strip()

    if output_dir == "":
        output_dir = get_downloads_folder()
        print(f"📁 Using Downloads folder: {output_dir}")

    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"❌ Could not create output directory: {e}")
        return

    if os.path.abspath(input_dir) == os.path.abspath(output_dir):
        print("❌ Input and output directories cannot be the same.")
        return

    print(f"\n📂 Input:  {input_dir}")
    print(f"📁 Output: {output_dir}")
    print(f"⚙️ Encoder: {VIDEO_ENCODER} | Quality: {VIDEO_QUALITY}\n")

    process_directory(input_dir, output_dir)

    print("\n✅ Done!")