# Batch Video Compressor

A simple Python tool to compress video files in a directory using **HandBrakeCLI**, while maintaining folder structure and copying non-video files.  
It dynamically tracks progress and skips videos that already exist in the output folder.

---

## Features

- Compresses videos using HandBrakeCLI with configurable encoder and quality.
- Supports `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`.
- Copies non-video files while preserving directory structure.
- Skips files already present in the output folder.
- Dynamic progress tracking (`[x/y]`) where skipped videos reduce the total.
- Default output folder is the user’s Downloads folder if none is specified.

---

## Prerequisites

1. **Python 3.x**  
2. **HandBrakeCLI**  

Download HandBrakeCLI from:  
[https://handbrake.fr/downloads2.php](https://handbrake.fr/downloads2.php)  

Place `HandBrakeCLI.exe` into the project directory (`BatchVideoCompressor`) or ensure it is in your system PATH.

---

## Setup

1. Clone or download this repository:

```bash
git clone <your-repo-url>
cd BatchVideoCompressor
```

2. Make sure the required Python modules are available (all standard library modules, no extra installation required):

```bash
Python standard libraries: os, shutil, subprocess
```

3. Verify that `HandBrakeCLI.exe` is in the same folder as the script or accessible via PATH.

---

## Usage

Run the script:

```bash
python batch_video_compressor.py
```

You will be prompted to enter:

1. **Input directory**: Path to the folder containing videos you want to compress.  
2. **Output directory**: Path where compressed videos will be saved.  
   - Leave blank to use the default Downloads folder.

Example:

```text
📂 Enter input directory: C:\Users\You\Videos
📁 Enter output directory (leave blank for Downloads): 
📁 Using Downloads folder: C:\Users\You\Downloads
```

---

## How it Works

- The script recursively walks through the input directory.  
- For each video file:
  - Compresses it with HandBrakeCLI using your configured encoder and quality.  
  - If the compressed file is larger, the original is kept.  
- For non-video files:
  - Copies them to the output directory while preserving folder structure.  
- Progress is displayed dynamically:
  
```text
🎯 Total videos found: 10
⏭️ Skipping (exists): video1.mp4 | New total: 9
[1/9] 🎬 Processing: video2.mkv
[2/9] 🎬 Processing: video3.mp4
```

---

## Configuration

At the top of the script you can modify:

```python
HANDBRAKE_PATH = r"HandBrakeCLI.exe"
VIDEO_ENCODER = "x264"       # CPU encoder
# VIDEO_ENCODER = "nvenc_h264" # GPU encoder (faster, larger files)
VIDEO_QUALITY = "24"         # Lower = higher quality
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv"}
```

---

## Notes / Tips

- **Do not commit `HandBrakeCLI.exe`**. Add it to `.gitignore`.  
- Avoid setting the **same input and output folder**, or the script will stop.  
- If you rerun the script, existing compressed videos will be skipped automatically.  
- Temporary `.tmp.mp4` files are removed automatically.  

---

## License

MIT License – Free to use and modify.