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

def generateOutputName(artist = False, song = False, album = False, date = False, track_pos = False, track_count = False):
    base = Path(config["download"]["output_dir"])
    template = config["download"]["output"]
    filled_template = template.format(
        artist=sanitize(artist),
        song=sanitize(song),
        album=sanitize(album),
        year=date,
        track_pos=track_pos,
        track_count=track_count,
    )

    path = base / Path(filled_template)
    log.debug(f'Output path: {str(path)}')
    return str(path)

def checkIfFileExists(artist, song):

    base = Path(config["download"]["output_dir"])
    template = config["download"]["output"] + ".*"
    
    filename = re.sub(r"\{(year|album|track_pos|track_count)\}", "*", template)

    filled_filepath = filename.format(
        artist=sanitize(artist),
        song=sanitize(song)
    )
    
    path = base / Path(filled_filepath)

    if glob.glob(str(path)):
        return True

    return False


#print(checkIfFileExists("Alexandra Căpitănescu", "Choke Me"))

