import os
import subprocess
import json
import re
import eyed3
import time

yt_dlp_path = r"C:\Users\Aviv\PycharmProjects\Car\spotify\yt-dlp.exe"
cookies_file = r"C:\Users\Aviv\PycharmProjects\Car\spotify\cookies.txt"
channel_url = "https://www.youtube.com/user/TheBeitHabubot/videos"

# שלב 1: משיכת JSON ראשון כדי לדעת את שם הערוץ/פלייליסט
print("📋 Fetching initial metadata...")
result = subprocess.run(
    [yt_dlp_path, "--cookies", cookies_file,
     "--flat-playlist", "--dump-json", "--playlist-start", "1", "--playlist-end", "1", channel_url],
    capture_output=True, text=True, check=True
)

video_data = json.loads(result.stdout.strip())
channel_or_playlist = video_data.get("playlist_title") or video_data.get("uploader") or "Unknown"
channel_or_playlist = re.sub(r'[\\/*?:"<>|]', "_", channel_or_playlist)

# יצירת תיקייה לפי שם הערוץ/פלייליסט
output_dir = rf"C:\yt-dlp\Downloaded\{channel_or_playlist}"
os.makedirs(output_dir, exist_ok=True)

# רשימת קבצים שכבר קיימים
existing_basenames = {
    os.path.splitext(f)[0] for f in os.listdir(output_dir)
    if f.lower().endswith(".mp3")
}

# שלב 2: משיכת רשימת הסרטונים המלאה
print(f"📋 Fetching full playlist for {channel_or_playlist}...")
result = subprocess.run(
    [yt_dlp_path, "--cookies", cookies_file,
     "--flat-playlist", "--dump-json", channel_url],
    capture_output=True, text=True, check=True
)

videos = [json.loads(line) for line in result.stdout.strip().split('\n')]
print(f"🎬 Found {len(videos)} videos.")

# הורדה של שירים
for video in videos:
    video_id = video.get("id")
    title = video.get("title")
    uploader = video.get("uploader") or video.get("playlist_uploader") or "Unknown"

    if not video_id or not title:
        print(f"⚠️ Skipping malformed video (missing id/title): {video}")
        continue

    expected_filename = f"{uploader} - {title}"
    if expected_filename in existing_basenames:
        print(f"⏩ Skipping existing: {expected_filename}")
        continue

    print(f"⬇️ Downloading: {expected_filename}")

    subprocess.run([
        yt_dlp_path,
        "--cookies", cookies_file,
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--output", f"{output_dir}\\%(uploader)s - %(title)s.%(ext)s",
        "--write-info-json",
        "--match-filter", "duration > 90 & duration < 420",
        f"https://www.youtube.com/watch?v={video_id}"
    ], check=True)

# תיוג הקבצים
for filename in os.listdir(output_dir):
    if not filename.lower().endswith(".mp3"):
        continue

    full_path = os.path.join(output_dir, filename)
    json_path = os.path.splitext(full_path)[0] + ".info.json"

    if not os.path.exists(json_path):
        print(f"⚠ Missing JSON for {filename}, skipping.")
        continue

    audio = eyed3.load(full_path)
    if audio and audio.tag and audio.tag.title:
        print(f"⏩ Skipping tagged file: {filename}")
        continue

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    original_title = data.get("title", "")
    parts = original_title.split(" - ")

    if len(parts) >= 3:
        artist = parts[0].strip()
        album = parts[1].strip()
        title = " - ".join(parts[2:]).strip()
        if title.endswith(artist):
            title = title[:-(len(artist))].strip(" -")
    elif len(parts) == 2:
        artist = parts[0].strip()
        album = ""
        title = parts[1].strip()
    else:
        artist = data.get("uploader", "")
        album = data.get("channel", "")
        title = original_title

    if audio is None:
        print(f"❌ Failed to load {filename}")
        continue

    if audio.tag is None:
        audio.initTag()

    audio.tag.title = title
    audio.tag.artist = artist
    audio.tag.album = album
    upload_date = data.get("upload_date", "")
    year = upload_date[:4] if len(upload_date) >= 4 else None
    if year and year.isdigit():
        audio.tag.recording_date = eyed3.core.Date(int(year))

    audio.tag.save(version=eyed3.id3.ID3_V2_3)
    os.remove(json_path)

    print(f"🎵 Tagged: {filename} | Title: {title} | Artist: {artist} | Album: {album} | Year: {year}")

print("🎉 All files downloaded and tagged successfully!")
