import os
import shutil
import config


from filesystem import process_directory


def get_downloads_folder() -> str:
    return os.path.join(os.path.expanduser("~"), "Downloads")


def choose_resolution_mode():
    print("\n🎞️ Compression resolution mode:")
    print("1. Keep original resolution")
    print("2. Compress to 1080p")
    print("3. Compress to 720p")
    print("4. Compress to 480p")

    while True:

        choice = input("Select option: ").strip()

        if choice == "1":
            config.TARGET_HEIGHT = None
            print("✅ Keeping original resolutions")
            return

        elif choice == "2":
            config.TARGET_HEIGHT = 1080
            print("✅ Target resolution: 1080p")
            return

        elif choice == "3":
            config.TARGET_HEIGHT = 720
            print("✅ Target resolution: 720p")
            return

        elif choice == "4":
            config.TARGET_HEIGHT = 480
            print("✅ Target resolution: 480p")
            return

        else:
            print("❌ Invalid option")


def main():
    if shutil.which(config.HANDBRAKE_PATH) is None and not os.path.isfile(config.HANDBRAKE_PATH):
        print("❌ HandBrakeCLI not found.")
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

    choose_resolution_mode()

    print(
        f"\n📂 Input:  {input_dir}"
        f"\n📁 Output: {output_dir}"
        f"\n⚙️ Encoder: {config.VIDEO_ENCODER} | Quality: {config.VIDEO_QUALITY}\n"
    )

    process_directory(input_dir, output_dir,)
    print("\n✅ Done!")


if __name__ == "__main__":
    main()