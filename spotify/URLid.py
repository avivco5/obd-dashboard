import subprocess
import json

yt_dlp_path = "yt-dlp"  # או הנתיב המלא

playlist_url = "https://www.youtube.com/user/TheBeitHabubot/videos"

# שלב 1: משיכת מזהים
result = subprocess.run(
    [yt_dlp_path, "--flat-playlist", "--dump-json", playlist_url],
    capture_output=True, text=True, check=True
)

videos = [json.loads(line) for line in result.stdout.strip().split('\n')]
print(f"🎬 Found {len(videos)} videos")

for video in videos:
    video_id = video.get("id")
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"🆔 {video_id} => {url}")
