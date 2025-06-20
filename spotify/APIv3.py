from flask import Flask, request, jsonify, render_template_string, Response
import os
import subprocess
import json
import re
import eyed3
import time

app = Flask(__name__)

YT_DLP_PATH = "yt-dlp"
BASE_OUTPUT_DIR = r"C:\\yt-dlp\\Downloaded"

PROFILE = "Profile 5"  # <-- קשיח לפרופיל 5


def wait_for_cookies_update(cookies_path, wait_msg="\u23f3 Waiting for cookies.txt update..."):
    last_mtime = os.path.getmtime(cookies_path)
    print(wait_msg)
    while True:
        time.sleep(3)
        if os.path.getmtime(cookies_path) > last_mtime:
            print("\u2705 cookies.txt updated. Resuming download.")
            break


@app.route("/", methods=['GET'])
def homepage():
    html = """
    <h2>🎵 YouTube Music Downloader</h2>
    <input type=\"text\" id=\"url\" placeholder=\"https://www.youtube.com/...\" size=\"60\"><br><br>
    <button onclick=\"download()\">Download</button>
    <pre id=\"response\" style=\"margin-top:20px; background:#eee; padding:10px;\"></pre>
    <script>
        function download() {
            const url = document.getElementById('url').value;
            fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('response').textContent = JSON.stringify(data, null, 2);
            })
            .catch(err => {
                document.getElementById('response').textContent = "\u274c Error: " + err;
            });
        }
    </script>
    """
    return Response(html, content_type='text/html; charset=utf-8')


@app.route("/download", methods=['POST'])
def download():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        # Fetch metadata
        result = subprocess.run([
    "yt-dlp",
    "--cookies-from-browser", "firefox",
    "--flat-playlist", "--dump-json",
    "--playlist-start", "1", "--playlist-end", "1",
    url
], capture_output=True, text=True, check=True)

        video_data = json.loads(result.stdout.strip())
        channel_or_playlist = video_data.get("playlist_title") or video_data.get("uploader") or "Unknown"
        channel_or_playlist = re.sub(r'[\\/*?:"<>|]', "_", channel_or_playlist)

        output_dir = os.path.join(BASE_OUTPUT_DIR, channel_or_playlist)
        os.makedirs(output_dir, exist_ok=True)

        existing_basenames = {
            os.path.splitext(f)[0] for f in os.listdir(output_dir) if f.lower().endswith(".mp3")
        }

        # Fetch all videos
        result = subprocess.run(
            [YT_DLP_PATH, "--cookies-from-browser", f"chrome:{PROFILE}",
             "--flat-playlist", "--dump-json", url],
            capture_output=True, text=True, check=True
        )
        videos = [json.loads(line) for line in result.stdout.strip().split('\n')]

        downloaded = []
        skipped = []

        for video in videos:
            video_id = video.get("id")
            title = video.get("title")
            uploader = video.get("uploader") or video.get("playlist_uploader") or "Unknown"
            if not video_id or not title:
                skipped.append(title or video_id or "<missing>")
                continue

            expected_filename = f"{uploader} - {title}"
            if expected_filename in existing_basenames:
                skipped.append(expected_filename)
                continue

            try:
                result = subprocess.run([
                    YT_DLP_PATH, "--cookies-from-browser", f"chrome:{PROFILE}",
                    "-x", "--audio-format", "mp3", "--audio-quality", "0",
                    "--output", f"{output_dir}\\%(uploader)s - %(title)s.%(ext)s",
                    "--write-info-json", "--match-filter", "duration > 90 & duration < 420",
                    f"https://www.youtube.com/watch?v={video_id}"
                ], capture_output=True, text=True)

                if "Sign in to confirm you" in result.stderr:
                    print(f"\u274c cookies expired for: {title}")
                    continue

                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=result.stderr)

                downloaded.append(expected_filename)
            except subprocess.CalledProcessError as e:
                skipped.append(f"Failed: {expected_filename} - {e.stderr.strip()[:100]}")

        # Tagging
        for filename in os.listdir(output_dir):
            if not filename.lower().endswith(".mp3"):
                continue
            full_path = os.path.join(output_dir, filename)
            json_path = os.path.splitext(full_path)[0] + ".info.json"
            if not os.path.exists(json_path):
                continue

            audio = eyed3.load(full_path)
            if audio and audio.tag and audio.tag.title:
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

        return jsonify({
            "status": "done",
            "downloaded": downloaded,
            "skipped": skipped,
            "folder": output_dir
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000)
