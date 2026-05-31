import requests
import time

import SomeDL.utils.console as console

def downloadAlbumArt(url: str):
    for attempt in range(2):  # --- initial request + 1 retry
        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                return response.content

        except requests.RequestException:
            pass

        if attempt == 0:
            console.warning("Failed to fetch album art: retrying")
            time.sleep(1)  # optional delay before retry

    console.error("Failed to fetch album art.")
    return False

