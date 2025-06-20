import os
import eyed3

folder_with_mp3 = r"C:\yt-dlp\Downloaded\DagNahash"

for filename in os.listdir(folder_with_mp3):
    if filename.lower().endswith(".mp3"):
        full_path = os.path.join(folder_with_mp3, filename)
        title = os.path.splitext(filename)[0]

        audio = eyed3.load(full_path)
        if audio is None:
            print(f"Failed to load {filename}")
            continue

        if audio.tag is None:
            audio.initTag()

        audio.tag.title = title
        audio.tag.save(version=eyed3.id3.ID3_V2_3)

        print(f"Updated {filename} with title '{title}'")
