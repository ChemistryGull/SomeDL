import requests

from SomeDL.utils.logging import log, printj


def downloadAlbumArt(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        log.error(" Could not find album art!")
        return False
    
    log.info("Successfully downloaded album art")
    return response.content

