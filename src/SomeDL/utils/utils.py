import re
import glob
from pathlib import Path

from SomeDL.utils.config import config


def sanitize(filename):
    if filename:
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
        return filename

def generateOutputName(artist = False, album_artist = False, song = False, album = False, date = False, track_pos = False, track_count = False):
    track_pos = str(track_pos).zfill(2)
    base = Path(config["download"]["output_dir"])
    template = config["download"]["output"]
    filled_template = template.format(
        artist=sanitize(artist),
        album_artist=sanitize(album_artist),
        song=sanitize(song),
        album=sanitize(album),
        year=date,
        track_pos=track_pos,
        track_count=track_count,
    )

    path = base / Path(filled_template)
    # print(f'Output path: {str(path)}')
    return str(path)

def read_archive_file():
    if not config["download"]["download_archive"]:
        return
        
    archive_path = Path(config["download"]["download_archive"])
    archive_path = archive_path.expanduser()
    archive_path = archive_path.resolve()

    if not archive_path.parent.exists():
        raise FileNotFoundError(f'Directory for the download archive does not exist, create it first: {archive_path.parent}')

    if not archive_path.exists():
        archive_path.touch()
        print(f'Created new download archive at: {str(archive_path)}')
        
    with open(archive_path, "r", encoding="utf-8") as f:
        config["download"]["download_archive_data"] = f.read().splitlines()


def checkIfFileExists(artist, song, song_id, album_artist = None):
    # TODO: implement a skip if --redownload is set

    if config["download"]["download_archive"]:
        if song_id in config["download"]["download_archive_data"]:
            return True

    if not config["download"]["check_if_file_exists"]:
        return False

    base = Path(config["download"]["output_dir"])
    template = config["download"]["output"] + ".*"
    
    filename = re.sub(r"\{(year|album|track_pos|track_count)\}", "*", template)

    if album_artist:
        # Full check with album_artist
        # filled_filepath = filename.format(
        #     artist=sanitize(artist),
        #     album_artist=sanitize(album_artist),
        #     song=sanitize(song)
        # )
        # print("first option")
        filename = re.sub(r"\{album_artist\}", sanitize(album_artist), filename)
        filename = re.sub(r"\{artist\}", sanitize(artist), filename)
        filled_filepath = re.sub(r"\{song\}", sanitize(song), filename)

    else:
        # Pre-check: wildcard album_artist so we don't need to fetch the album
        # filename = re.sub(r"\{album_artist\}", "*", filename)
        # filled_filepath = filename.format(
        #     artist=sanitize(artist),
        #     song=sanitize(song)
        # )
        # print("second option")
        filename = re.sub(r"\{album_artist\}", sanitize(artist), filename)
        filename = re.sub(r"\{artist\}", sanitize(artist), filename)
        filled_filepath = re.sub(r"\{song\}", sanitize(song), filename)
        

    # filled_filepath = filename.format(
    #     artist=sanitize(artist),
    #     song=sanitize(song)
    # )
    # print(filled_filepath)
    path = base / Path(filled_filepath)
    path_str = re.sub(r'[\[\]]', lambda m: '[[]' if m.group() == '[' else '[]]', str(path))
    # print(path_str)
    if glob.glob(path_str):
        return True

    return False


def clean_song_title(song_title: str):
    # removable_patterns = r'\b(feat\.?|featuring|ft\.?|with|remaster(ed)?|re-?master(ed)?|deluxe|edition|version|remix|radio\s*edit|single\s*edit|bonus\s*track|explicit|clean|original\s*mix|extended\s*mix|instrumental)\b'
    removable_patterns = r'\b(feat\.?|featuring|ft\.?|remaster(ed)?|re-?master(ed)?)\b'

    return re.sub(r'\([^)]*\)', lambda m: '' if re.search(removable_patterns, m.group(), re.IGNORECASE) else m.group(), song_title).strip()


# print(clean_song_title("Initiation (2024 Remastered lolo)"))
# print(clean_song_title("Delain Queen of Shadow (feat. Paolo Ribaldini)"))
# print(clean_song_title("Delain Queen of Shadow (Paolo Ribaldini)"))
# print(clean_song_title("Delain Queen of Shadow (or with you)"))
# print(clean_song_title("Delain Queen of Shadow (or without you)"))
# print(clean_song_title("Delain Queen of Shadow (radio)"))
# print(clean_song_title("Delain Queen of Shadow (edit)"))
# print(clean_song_title("Delain Queen of Shadow (radio edit)"))

# print(checkIfFileExists("Alexandra Căpitănescu", "Choke Me"))
# print(checkIfFileExists("Delain & sb", "Moth to a Flame", "Delain"))

# print(checkIfFileExists("Delain [band]", "Sleepwalkers Dream", "Delain [band]"))
# print(checkIfFileExists("Delain (band)", "Sleepwalkers Dream", "Delain (band)"))
# print(checkIfFileExists("Delain ", "Sleepwalkers Dream", "Delain "))