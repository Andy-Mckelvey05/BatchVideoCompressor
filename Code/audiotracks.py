import re
import subprocess

import config


AUDIO_PENALTIES = {
    "commentary": -100,
    "comment": -100,
    "director": -100,
    "descriptive": -100,
    "description": -100,
    "audio description": -100,
    "narration": -80,
    "narrator": -80,
    "alternate": -50,
    "alternative": -50,
    "karaoke": -100,
    "isolated": -100,
}


AUDIO_BONUSES = {"original": 20, "main": 20,}


def scan_audio_tracks(input_path: str) -> list:
    cmd = [
        str(config.HANDBRAKE_PATH),
        "--scan",
        "-i",
        input_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )

    except Exception as e:
        print(f"⚠️ Could not scan audio tracks: {e}")
        return []

    output = result.stdout

    tracks = []

    in_audio_section = False

    for line in output.splitlines():
        if line.strip() == "+ audio tracks:":
            in_audio_section = True
            continue

        if line.strip().startswith("+ subtitle tracks:"):
            break

        if not in_audio_section:
            continue

        match = re.match(
            r"^\s*\+\s*(\d+),\s*(.*?)" r"\s*\(iso639-2:\s*([a-z]{3})\)\s*$", line, re.IGNORECASE,)

        if not match:
            continue

        track_number = int(match.group(1))
        description = match.group(2).strip()
        language = match.group(3).lower()

        channels = detect_channels(description)
        bitrate = detect_bitrate(description)

        tracks.append(
            {
                "track": track_number,
                "language": language,
                "description": description,
                "channels": channels,
                "bitrate": bitrate,
            }
        )

    return tracks


def detect_channels(description: str) -> int:
    match = re.search(r"(\d+(?:\.\d+)?)\s*ch", description, re.IGNORECASE)

    if not match:
        return 0

    layout = match.group(1)

    try:
        if layout == "2.0":
            return 2
        if layout == "5.1":
            return 6
        if layout == "7.1":
            return 8

        return int(float(layout))

    except ValueError:
        return 0


def detect_bitrate(description: str) -> int:
    match = re.search(r"(\d+)\s*kbps", description, re.IGNORECASE)

    if not match:
        return 0

    return int(match.group(1))


def score_audio_track(track: dict) -> int:
    description = track["description"].lower()
    language = track["language"]

    score = 0

    if language == "eng":
        score += 100
    elif language == "und":
        score += 0
    else:
        score -= 20

    for word, points in AUDIO_PENALTIES.items():
        if word in description:
            score += points

    for word, points in AUDIO_BONUSES.items():
        if word in description:
            score += points

    channels = track["channels"]

    if channels >= 8:
        score += 30
    elif channels >= 6:
        score += 25
    elif channels >= 2:
        score += 10
    elif channels == 1:
        score -= 10

    bitrate = track["bitrate"]

    if bitrate >= 640:
        score += 10

    elif bitrate >= 384:
        score += 5

    return score


def choose_audio_track(input_path: str):
    tracks = scan_audio_tracks(input_path)

    if not tracks:
        print("⚠️ No audio tracks detected.")
        return None

    print("\n🎧 Audio tracks detected:")

    for track in tracks:
        print(
            f"  Track {track['track']}: "
            f"{track['language']} | "
            f"{track['description']}"
        )

    selected = max(tracks, key=score_audio_track)

    print(
        f"\n🎵 Selected audio track:\n"
        f"  {selected['track']} | "
        f"{selected['language']} | "
        f"{selected['description']}"
    )

    return selected["track"]