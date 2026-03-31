import re
import requests

import SomeDL.utils.console as console
from SomeDL.utils.config import config
from SomeDL.utils.version import VERSION


lrclib_headers = {
    "User-Agent": f"SomeDL/{VERSION} (https://github.com/ChemistryGull/SomeDL)"
}

def lrclib_get_lyrics(artist: str, song: str, album: str = None, duration: int = None, label: str = None):
    # timerstart("lrclib")

    URL = f'https://lrclib.net/api/get?artist_name={artist}&track_name={song}'
    if album:
        URL += f'&album_name={album}'
    if duration:
        URL += f'&duration={duration}'


    try:
        response = requests.get(URL, headers=lrclib_headers)
    except Exception as e:
        console.error("Lyrics: Error while trying to reach lrclib.net. Error:", label)
        console.error(e, label)
        console.update(label, "get_lyrics", console.Status.FAILED)
        return False


    # timerend("lrclib")
    # printj(response.json())
    if response.status_code == 200:
        
        data = response.json()
        return data
        # return {
        #     "plain": data.get("plainLyrics"),
        #     "synced": data.get("syncedLyrics"),
        # }
    elif response.status_code == 404:
        console.debug("lrclib lyrics not found.", label)
    else:
        console.error(f"Lyrics: lrclib error: {response.status_code}")
        console.update(label, "get_lyrics", console.Status.FAILED)
        return False
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
