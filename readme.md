# Batch Video Compressor

A Python-based batch video compression tool using HandBrakeCLI and x264 CPU encoding.

The tool recursively processes a folder of videos, preserves the original folder structure, copies non-video files, and intelligently decides how each video should be compressed.

It can optionally reduce videos to a maximum resolution of 1080p, 720p, or 480p.

---

## Features

- 🎬 Batch compresses videos using HandBrakeCLI.
- 🖥️ Uses x264 CPU encoding for the final compression.
- ⚡ Uses NVIDIA NVENC GPU encoding as a quick compression test when appropriate.
- 🧠 Automatically decides whether the GPU test is worthwhile.
- 📉 Supports maximum output resolutions of:
  - Original resolution
  - 1080p
  - 720p
  - 480p
- 🚫 Never upscales videos.
- 📁 Recursively preserves the original folder structure.
- 📄 Copies non-video files to the output directory.
- 📊 Displays processing progress.
- 📥 Defaults to the user's Downloads folder when no output directory is provided.
- 🔧 Uses only Python standard-library modules; no pip packages are required.

---

## Supported Video Formats

The following file extensions are processed as videos:
- .mp4
- .mkv
- .avi
- .mov
- .wmv

Other files are treated as regular files and are copied to the output directory. Preserving the folder structure.

---

## How Compression Works

The compression process depends on the selected resolution mode.

### Keep Original Resolution

If Keep original resolution is selected, the source video's resolution is not changed.

The tool first performs a GPU test encode to determine whether compression is likely to reduce the file size.

The process is:
1. The original video is measured.
2. A temporary GPU encode is created using NVIDIA NVENC.
3. The GPU output size is compared with the original file.
4. If the GPU result is too large, the original video is kept.
5. If the GPU result is an acceptable size, the temporary GPU file is deleted.
6. The video is then encoded using x264 CPU encoding for the final output.

| GPU Test Result                | Action                  |
|--------------------------------|-------------------------|
| GPU file is too large          | Keep the original video |
| GPU file is an acceptable size | Run the CPU x264 encode |

---

### Target Resolution Selected

When 1080p, 720p, or 480p is selected, the source resolution is checked before compression.

The tool compares the source video's height against the selected target height.

#### Source Is Larger Than Target

If the source video is larger than the selected target resolution, the video must be downscaled.

In this situation, the GPU test is skipped because there is no need to test whether the original-resolution GPU encode will save space. The video is already going to be reduced in resolution.

The process is:
1. Detect the source resolution.
2. Compare the source height with the target height.
3. If the source is larger, prepare the resize settings.
4. Skip the GPU test.
5. Encode directly using x264 CPU encoding.

For example, if 480p is selected and the source is 1080p:

1080p → 480p → x264 CPU encode

---

#### Source Is Already At or Below Target

If the source video is already at or below the selected target resolution, the video is not resized.

The normal GPU test is then performed.

The process is:

1. Detect the source resolution.
2. Compare the source height with the target height.
3. If the source is already at or below the target, do not resize it.
4. Run the GPU test encode.
5. Compare the GPU output size with the original.
6. Keep the original if the GPU result is too large.
7. Otherwise, perform the final x264 CPU encode.

---

### Compression Decision Summary

| Situation                  | Resize? | GPU Test? | Final Action                      |
|----------------------------|--------:|----------:|-----------------------------------|
| Keep original resolution   |      No |       Yes | GPU test → CPU encode or original |
| Source above target        |     Yes |        No | CPU encode                        |
| Source equal to target     |      No |       Yes | GPU test → CPU encode or original |
| Source below target        |      No |       Yes | GPU test → CPU encode or original |
| Resolution detection fails | Unknown |       Yes | Normal GPU test workflow          |

---

### Example: 480p Target

If 480p is selected, the behavior is:

| Source Resolution | Resize | GPU Test | Result                                 |
|-------------------|-------:|---------:|----------------------------------------|
| 2160p             |    Yes |       No | Downscale to 480p → CPU encode         |
| 1440p             |    Yes |       No | Downscale to 480p → CPU encode         |
| 1080p             |    Yes |       No | Downscale to 480p → CPU encode         |
| 720p              |    Yes |       No | Downscale to 480p → CPU encode         |
| 480p              |     No |      Yes | GPU test → CPU encode or keep original |
| 360p              |     No |      Yes | GPU test → CPU encode or keep original |

The tool will never upscale a video. A video that is already below the selected target resolution will retain its original resolution.

---

## Prerequisites

You need:
1. Python 3.x
2. HandBrakeCLI
3. An NVIDIA GPU is optional. The GPU test is only used when available and applicable.

Download HandBrakeCLI from:
https://handbrake.fr/downloads2.php

Place HandBrakeCLI.exe in the main project directory:

text BatchVideoCompressor/ ├── HandBrakeCLI.exe └── Code/ 

The application automatically finds HandBrakeCLI.exe relative to the project directory.

---

### Python Modules

| File          | Purpose                                        |
|---------------|------------------------------------------------|
| main.py       | Handles user input and starts the application  |
| config.py     | Contains application configuration             |
| compressor.py | Controls compression decisions and workflow    |
| encoder.py    | Contains GPU and CPU HandBrake encoding        |
| filesystem.py | Handles directory traversal and file copying   |
| video.py      | Detects video files and reads video resolution |

---

## Setup

Clone or download the repository:

bash git clone <your-repo-url> cd BatchVideoCompressor 

No additional Python packages are required. The project uses Python's standard library.

Make sure HandBrakeCLI.exe is located in the root project directory.

---

## Resolution Modes

### 1. Keep Original Resolution

Videos retain their original resolution.

The GPU test is performed to determine whether compression is likely to reduce the file size. If the GPU result is too large, the original file is kept.

### 2. Compress to 1080p

Videos above 1080p are downscaled to a maximum height of 1080 pixels.

Videos already at or below 1080p are not upscaled.

### 3. Compress to 720p

Videos above 720p are downscaled to a maximum height of 720 pixels.

Videos already at or below 720p are not upscaled.

### 4. Compress to 480p

Videos above 480p are downscaled to a maximum height of 480 pixels.

Videos already at or below 480p are not upscaled.

---

## Notes

- HandBrakeCLI.exe should be kept in the project root.
- Do not use the input directory as the output directory.
- Resolution targeting never upscales a video.
- Downscaling videos skip the GPU test and go directly to CPU encoding.
- Temporary GPU test files are deleted after the test.

---

## License

MIT License – Free to use and modify.