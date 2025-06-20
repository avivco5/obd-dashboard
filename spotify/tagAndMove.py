import os
import shutil
from mutagen.easyid3 import EasyID3
import subprocess

artist_map = {
    "dennis lloyd": "Dennis Lloyd",
    "dennislloyd": "Dennis Lloyd",
    "noa kirel": "נועה קירל",
    "נועה קירל": "נועה קירל",
    "osher cohen": "אושר כהן",
    "oshercohen": "אושר כהן",
    "אושר כהן": "אושר כהן",
    "eden hason": "עדן חסון",
    "עדן חסון": "עדן חסון",
    "cookie levanna": "קוקי לבנה",
    "קוקי לבנה": "קוקי לבנה"
}


def normalize_artist(artist_name):
    key = artist_name.strip().lower()
    return artist_map.get(key, artist_name)


def unify_tags_and_copy(src_folder, dst_folder):
    os.makedirs(dst_folder, exist_ok=True)
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.lower().endswith(".mp3"):
                full_path = os.path.join(root, file)
                try:
                    tags = EasyID3(full_path)
                    artist = tags.get('artist', [None])[0]
                    if artist:
                        unified_artist = normalize_artist(artist)
                        if artist != unified_artist:
                            tags['artist'] = unified_artist

                    title_from_filename = os.path.splitext(file)[0]
                    tags['title'] = title_from_filename
                    tags.save()

                    subprocess.run([
                        "eyeD3", "--to-v2.3",
                        full_path
                    ], check=True)

                    dst_path = os.path.join(dst_folder, file)
                    shutil.copy2(full_path, dst_path)

                    print(f"Processed and copied '{file}'")
                except Exception as e:
                    print(f"Failed to process {file}: {e}")


source_folder = "/media/sf_Downloaded"
destination_folder = "/opt/navidrome/music"

unify_tags_and_copy(source_folder, destination_folder)
