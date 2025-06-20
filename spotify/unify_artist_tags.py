from mutagen.easyid3 import EasyID3
import os

# מיפוי איחוד שמות אומנים
artist_map = {
    "dennis lloyd": "Dennis Lloyd",
    "dennislloyd": "Dennis Lloyd",

    "noa kirel": "נועה קירל",
    "נועה קירל": "נועה קירל",

    "osher cohen": "אושר כהן",
    "oshercohen": "אושר כהן",
    "אושר כהן": "אושר כהן",

    "eden hason": "עדן חסון",
    "eden hason": "עדן חסון",
    "עדן חסון": "עדן חסון",

    "cookie levanna": "קוקי לבנה",
    "קוקי לבנה": "קוקי לבנה"
}

def normalize_artist(artist_name):
    key = artist_name.strip().lower()
    return artist_map.get(key, artist_name)

def unify_artist_tags_in_folder(folder_path):
    for root, _, files in os.walk(folder_path):
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
                            tags.save()
                            print(f"Updated artist in '{file}': '{artist}' -> '{unified_artist}'")
                except Exception as e:
                    print(f"Failed to update {file}: {e}")

# שימוש:
folder_with_mp3 = r"C:\yt-dlp\NewDownloaded"
unify_artist_tags_in_folder(folder_with_mp3)
