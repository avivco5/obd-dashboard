import os
import subprocess
import json
from pathlib import Path

yt_dlp = "yt-dlp.exe"
input_file = "youtube_links.txt"
dest_dir = Path("Downloaded")
archive_file = "downloaded.txt"

dest_dir.mkdir(exist_ok=True)

with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        url = line.strip()
        if not url or url.startswith('#'):
            continue
        print(f"⬇️ Downloading from: {url}")
        subprocess.run([
            yt_dlp,
            "-x", "--audio-format", "mp3", "--audio-quality", "0",
            "--output", f"{dest_dir}/%(uploader)s - %(title)s.%(ext)s",
            "--download-archive", archive_file,
            "--write-info-json",
            url
        ])

print("\n🏷️ Tagging files...")
for mp3_file in dest_dir.glob("*.mp3"):
    json_file = mp3_file.with_suffix(".info.json")
    if json_file.exists():
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
            title = data.get("title", mp3_file.stem)
            artist = data.get("uploader", "Unknown")
            album = data.get("channel", "YouTube")
            year = data.get("upload_date", "0000")[:4]

            subprocess.run([
                "eyeD3",
                "--title", title,
                "--artist", artist,
                "--album", album,
                "--release-year", year,
                str(mp3_file)
            ])
        json_file.unlink()
    else:
        print(f"⚠️ No JSON for {mp3_file.name} – skipping")

print("\n✅ All done. Files are ready in 'Downloaded'")
