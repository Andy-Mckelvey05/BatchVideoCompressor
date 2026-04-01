import os
import shutil
import subprocess

# ========= CONFIG =========
HANDBRAKE_PATH = r"HandBrakeCLI.exe"

VIDEO_ENCODER = "x264"  # CPU encoding (slower, better compression)
VIDEO_QUALITY = "24"

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv"}
# ==========================


def is_video(file_name: str) -> bool:
    return os.path.splitext(file_name)[1].lower() in VIDEO_EXTENSIONS

def encode_gpu(input_path: str, output_path: str) -> bool:
    cmd = [
        HANDBRAKE_PATH,
        "-i", input_path,
        "-o", output_path,
        "--format", "av_mp4",
        "--encoder", "nvenc_h264",
        "--quality", VIDEO_QUALITY,
        "--rate", "auto",
        "--vfr",
        "--all-audio",
        "--aencoder", "copy",
        "--all-subtitles",
    ]

    try:
        creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)

        subprocess.run(
            cmd,
            check=True,
            creationflags=creation_flags,
        )

        return os.path.exists(output_path)

    except subprocess.CalledProcessError as e:
        print(f"❌ GPU encode failed: {e}")
        return False

def compress_video(input_path: str, output_path: str):
    gpu_tmp = output_path + ".gpu.mp4"
    cpu_tmp = output_path + ".cpu.mp4"

    print(f"\n🎬 Processing:\n{input_path}")

    print("⚡ Running GPU test encode...")
    if not encode_gpu(input_path, gpu_tmp):
        print("❌ GPU encode failed, falling back to copy")
        shutil.copy2(input_path, output_path)
        return

    original_size = os.path.getsize(input_path)
    gpu_size = os.path.getsize(gpu_tmp)

    if gpu_size >= original_size:
        print("⏭️ GPU result larger — skipping CPU encode, copying original")
        os.remove(gpu_tmp)
        shutil.copy2(input_path, output_path)
        return

    print("✅ GPU shows potential savings → running CPU encode...")

    # 🔥 NEW: delete GPU file early to free space
    try:
        os.remove(gpu_tmp)
    except Exception as e:
        print(f"⚠️ Could not delete GPU temp file early: {e}")

    cmd = [
        HANDBRAKE_PATH,
        "-i", input_path,
        "-o", cpu_tmp,
        "--format", "av_mp4",
        "--optimize",
        "--markers",
        "--encoder", "x264",
        "--quality", VIDEO_QUALITY,
        "--rate", "auto",
        "--vfr",
        "--encoder-preset", "fast",
        "--all-audio",
        "--aencoder", "copy",
        "--all-subtitles",
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("❌ CPU encode failed, falling back to original")
        shutil.copy2(input_path, output_path)
        return

    os.replace(cpu_tmp, output_path)

    print("✅ CPU encode complete (best compression)")

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
                print(f"\n[{processed_videos}/{total_videos} | {percentage}%] 🎬 Processing:")
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

    while True:
        input_dir = input("📂 Enter input directory: ").strip()
        if os.path.exists(input_dir):
            break
        print("❌ Invalid path, try again.\n")

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