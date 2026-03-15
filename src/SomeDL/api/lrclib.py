
import re
import requests

from SomeDL.utils.logging import log, printj, timerstart, timerend
from SomeDL.utils.config import config
from SomeDL.utils.version import VERSION


lrclib_headers = {
    "User-Agent": f"SomeDL/{VERSION} (https://github.com/ChemistryGull/SomeDL)"
}

def lrclib_get_lyrics(artist: str, song: str, album: str = None, duration: int = None):
    timerstart("lrclib")
    URL = "https://lrclib.net/api/get"
    params = {
        "artist_name": artist,
        "track_name": song,
    }
    if album:
        params["album_name"] = album
    if duration:
        params["duration"] = duration

    response = requests.get(URL, params=params, headers=lrclib_headers)

    timerend("lrclib")
    # printj(response.json())
    if response.status_code == 200:
        
        data = response.json()
        return data
        # return {
        #     "plain": data.get("plainLyrics"),
        #     "synced": data.get("syncedLyrics"),
        # }
    elif response.status_code == 404:
        log.debug("lrclib lyrics not found.")
    else:
        log.debug(f"lrclib error: {response.status_code}")
    return {}

# timerstart("lrclib")
# printj(lrclib_get_lyrics("lordi", "hard rock halleluja", duration=180))
# timerend("lrclib")

# arr = [
#     "hello [abcdefghij] world",
#     "test [1234567890]",
#     "invalid [short]",
#     "another [eora97eee12] example",
#     "no brackets here"
# ]

# pattern = re.compile(r"\[[^\]]{10}\]")

# matches = [s for s in arr if pattern.search(s)]

# print(matches)
