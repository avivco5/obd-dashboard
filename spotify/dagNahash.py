import eyed3
import time
import os
import subprocess
import json

yt_dlp_path = r"C:\Users\Aviv\PycharmProjects\Car\spotify\yt-dlp.exe"
cookies_file = r"C:\Users\Aviv\PycharmProjects\Car\spotify\cookies.txt"
output_dir = r"C:\yt-dlp\Downloaded\DagNahash"
channel_url = "https://www.youtube.com/channel/UCbMRbnFXUr9oyB28c24ST5Q/videos"

os.makedirs(output_dir, exist_ok=True)

# שלב 1: רשימת קבצים שכבר קיימים
existing_basenames = {
    os.path.splitext(f)[0] for f in os.listdir(output_dir)
    if f.lower().endswith(".mp3")
}

# שלב 2: משיכת רשימת וידאוים מבלי להוריד
print("📋 Fetching video list...")
result = subprocess.run(
    [yt_dlp_path, "--cookies", cookies_file,
     "--flat-playlist", "--dump-json", "--playlist-start", "42", channel_url],
    capture_output=True, text=True, check=True
)

videos = [json.loads(line) for line in result.stdout.strip().split('\n')]
print(f"🎬 Found {len(videos)} videos starting from index 42.")

# שלב 3: הורדה של כל שיר שאין לו קובץ קיים
for video in videos:
    video_id = video.get("id")
    title = video.get("title")
    uploader = video.get("uploader")

    if not video_id or not title or not uploader:
        print(f"⚠️ Skipping malformed video: {video}")
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

print("✅ Download complete!")

# תיוג הקבצים שהורדו
for filename in os.listdir(output_dir):
    if not filename.lower().endswith(".mp3"):
        continue

    full_path = os.path.join(output_dir, filename)
    json_path = os.path.splitext(full_path)[0] + ".info.json"

    if not os.path.exists(json_path):
        print(f"⚠ Missing JSON for {filename}, skipping.")
        continue

    # דילוג אם כבר יש תגיות
    audio = eyed3.load(full_path)
    if audio and audio.tag and audio.tag.title:
        print(f"⏩ Skipping tagged file: {filename}")
        continue

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    original_title = data.get("title", "")
    artist = data.get("uploader", "")
    album = data.get("channel", "")
    upload_date = data.get("upload_date", "")
    year = upload_date[:4] if len(upload_date) >= 4 else None

    # ✂️ חיתוך הטייטל – רק החלק השלישי ואילך
    parts = original_title.split(" - ")

    if len(parts) >= 3:
        artist = parts[0].strip()
        album = parts[1].strip()
        title = " - ".join(parts[2:]).strip()

        # הסרת שם האמן מהסוף אם חוזר
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

    if year and year.isdigit():
        audio.tag.recording_date = eyed3.core.Date(int(year))

    audio.tag.save(version=eyed3.id3.ID3_V2_3)
    os.remove(json_path)

    print(f"🎵 Tagged: {filename} | Title: {title} | Artist: {artist} | Album: {album} | Year: {year}")

print("🎉 All files tagged successfully!")
