import requests

import SomeDL.utils.console as console

def downloadAlbumArt(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        return False
        
    return response.content

