import json
import csv
import sys
import subprocess
from pathlib import Path

# METADATA


import csv
import json
import subprocess
import sys
from pathlib import Path

from httpx import stream

# 1. Get the folder path from the terminal
folder=Path(
    "/Users/camilacastano/Desktop/cataracts1/gathering_info"
).expanduser().resolve()

if not folder.is_dir():
    sys.exit(f"Folder not found: {folder}")

# 2. Find all MP4 files, including files in subfolders
videos = sorted(
    file for file in folder.rglob("*")
    if file.is_file() and file.suffix.lower() == ".mp4"
)

if not videos:
    sys.exit(f"No MP4 files found in {folder}")

# 3. Extract metadata from each video

rows = []

for video in videos:
    print(f"Processing: {video.name}")

    row = {
        "file_name": video.name,
        "relative_path": str(video.relative_to(folder)),
        "size_MB": round(video.stat().st_size / (1024 ** 2), 2),
        "container_format": "",
        "duration_seconds": "",
        "width_px": "",
        "height_px": "",
        "resolution": "",
        "frame_rate_fps": "",
        "frame_count": "",
        "video_codec": "",
        "overall_bitrate_kbps": "",
        "status": "OK",
        "error": ""
    }

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-count_frames",
                "-show_format",
                "-show_streams",
                "-of", "json",
                str(video)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)
        video_format = data.get("format", {})

        # Container format
        row["container_format"] = video_format.get(
            "format_name", ""
        )

        # Duration in seconds
        duration = video_format.get("duration")
        if duration is not None:
            row["duration_seconds"] = round(float(duration), 3)

        # Overall bitrate in kilobits per second
        bitrate = video_format.get("bit_rate")
        if bitrate is not None:
            row["overall_bitrate_kbps"] = round(
                int(bitrate) / 1000, 2
            )

        # Find the main video stream
        stream = next(
            (
                s for s in data.get("streams", [])
                if s.get("codec_type") == "video"
            ),
            None
        )

        if stream is None:
            raise ValueError("No video stream found")

        # Width and height in pixels
        width = stream.get("width")
        height = stream.get("height")

        row["width_px"] = width if width is not None else ""
        row["height_px"] = height if height is not None else ""

        # Combined resolution
        if width is not None and height is not None:
            row["resolution"] = f"{width}x{height}"

        # Frame rate
        frame_rate = stream.get("avg_frame_rate", "0/1")

        if "/" in frame_rate:
            numerator, denominator = frame_rate.split("/")

            if float(denominator) != 0:
                row["frame_rate_fps"] = round(
                    float(numerator) / float(denominator), 3
                )

        # Video codec
        row["video_codec"] = stream.get("codec_name", "")

        # Total frame count
        # Prefer frames counted by FFprobe; fall back to
        # the frame count recorded in the metadata.
        frame_count = stream.get("nb_read_frames")

        if frame_count in (None, "N/A"):
            frame_count = stream.get("nb_frames")

        if frame_count not in (None, "N/A"):
            row["frame_count"] = int(frame_count)

    except Exception as error:
        row["status"] = "ERROR"
        row["error"] = str(error)

    rows.append(row)


# 4. Save the results as a CSV table
output = folder / "video_metadata.csv"

columns = [
    "file_name",
    "relative_path",
    "size_MB",
    "container_format",
    "duration_seconds",
    "width_px",
    "height_px",
    "resolution",
    "frame_rate_fps",
    "frame_count",
    "video_codec",
    "overall_bitrate_kbps",
    "status",
    "error"
]

with output.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

# 5. Display the final result
print(f"\nFinished: {len(rows)} video(s) processed.")
print(f"Metadata table saved to: {output}")




# try to automate the process after this testing
# lets use also MoviePy

