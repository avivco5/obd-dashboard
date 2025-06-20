import os
from mutagen.easyid3 import EasyID3

folder_with_mp3 = r"C:\yt-dlp\Downloaded\DagNahash"

for filename in os.listdir(folder_with_mp3):
    if filename.lower().endswith(".mp3"):
        full_path = os.path.join(folder_with_mp3, filename)
        try:
            tags = EasyID3(full_path)
            title = tags.get("title", ["Unknown Title"])[0]
            artist = tags.get("artist", ["Unknown Artist"])[0]
            album = tags.get("album", ["Unknown Album"])[0]

            print(f"File: {filename}")
            print(f" Title: {title}")
            print(f" Artist: {artist}")
            print(f" Album: {album}")
            print("-" * 40)

        except Exception as e:
            print(f"Error reading {filename}: {e}")
