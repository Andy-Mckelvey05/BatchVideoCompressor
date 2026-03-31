import os
import shutil
import subprocess

# ========= CONFIG =========
HANDBRAKE_PATH = r"HandBrakeCLI.exe"

VIDEO_ENCODER = "x264"  # CPU encoding (slower, better compression)
# VIDEO_ENCODER = "nvenc_h264"  # GPU encoding (faster, larger files)

VIDEO_QUALITY = "24"

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv"}
# ==========================


def is_video(file_name: str) -> bool:
    return os.path.splitext(file_name)[1].lower() in VIDEO_EXTENSIONS


def compress_video(input_path: str, output_path: str):
    """
    Compress a video using HandBrakeCLI.
    Falls back to copying if compression is not beneficial.
    """
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

    cmd = [str(x) for x in cmd]

    print(f"\n🎬 Compressing:\n{input_path}")

    try:
        creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        subprocess.run(
            cmd,
            check=True,
            creationflags=creation_flags,
        )

    except subprocess.CalledProcessError:
        print(f"❌ Compression failed: {input_path}")
        return

    if not os.path.exists(tmp_output):
        print(f"❌ Output not created: {input_path}")
        return

    try:
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(tmp_output)

        if compressed_size >= original_size:
            print("⏭️ No size benefit — keeping original")
            shutil.copy2(input_path, output_path)
            os.remove(tmp_output)
        else:
            os.replace(tmp_output, output_path)
            saved = original_size - compressed_size
            print(f"✅ Saved {saved} bytes → {output_path}")

    except Exception as e:
        print(f"❌ File handling error: {e}")
        if os.path.exists(tmp_output):
            os.remove(tmp_output)


def count_videos(input_dir: str) -> int:
    total = 0
    for root, _, files in os.walk(input_dir):
        for file in files:
            if is_video(file):
                total += 1
    return total

def process_directory(input_dir: str, output_dir: str):
    total_videos = count_videos(input_dir)
    remaining_videos = total_videos
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
                if os.path.exists(output_file):
                    remaining_videos -= 1
                    print(f"⏭️ Skipping (exists): {output_file} | New total: {remaining_videos}")
                    continue

                # Update processed count
                processed_videos += 1
                print(f"[{processed_videos}/{remaining_videos}] 🎬 Processing:")
                compress_video(input_file, output_file)

            else:
                output_copy = os.path.join(output_root, file)
                if os.path.exists(output_copy) and os.path.getsize(output_copy) > 0:
                    print(f"⏭️ Skipping copy: {output_copy}")
                    continue

                print(f"📄 Copying: {input_file}")
                shutil.copy2(input_file, output_copy)


def get_downloads_folder() -> str:
    return os.path.join(os.path.expanduser("~"), "Downloads")


def main():
    # Validate HandBrakeCLI exists
    if shutil.which(HANDBRAKE_PATH) is None and not os.path.isfile(HANDBRAKE_PATH):
        print("❌ HandBrakeCLI not found. Make sure it's installed or the path is correct.")
        return

    print("📥 Video Compression Tool\n")

    # --- Input directory ---
    while True:
        input_dir = input("📂 Enter input directory: ").strip()
        if os.path.exists(input_dir):
            break
        print("❌ Invalid path, try again.\n")

    # --- Output directory ---
    output_dir = input("📁 Enter output directory (leave blank for Downloads): ").strip()
    if not output_dir:
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

if __name__ == "__main__":
    main()