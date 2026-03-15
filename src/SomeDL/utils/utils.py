import re
import glob
from pathlib import Path
import timeit
from SomeDL.utils.config import config
from SomeDL.utils.logging import log, timerstart, timerend

def sanitize(filename):
    # Define a whitelist of allowed characters (alphanumeric, spaces, hyphens, underscores, etc.)
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
    log.debug(f'Output path: {str(path)}')
    return str(path)

def checkIfFileExists(artist, song, album_artist = None):

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

    if glob.glob(str(path)):
        return True

    return False


# print(checkIfFileExists("Alexandra Căpitănescu", "Choke Me"))
# print(checkIfFileExists("Delain & sb", "Moth to a Flame", "Delain"))

