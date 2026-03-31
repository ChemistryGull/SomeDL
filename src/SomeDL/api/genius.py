import requests
import json
import time

# from SomeDL.utils.logging import log
from SomeDL.utils.config import config

genius_headers = {
    "Authorization": f'Bearer {config["api"]["genius_token"]}'
}

def geniusGetAlbumBySongName(artist: str, song: str, label: str = None):
    # --- This gets the album name based on an artist and an album query with two API requests at the official Genius API (needs token)
    # TODO: Better error handling! probably crashes the program when problem
    # --- Public API (no auth): https://genius.com/api/
    # --- Official API (auth): https://api.genius.com/
    if config["api"]["genius_use_official"]:
        api_base = "api.genius.com"
        g_headers = genius_headers
    else:
        api_base = "genius.com/api"
        g_headers = {}

    url = f'https://{api_base}/search?q={artist} {song}' 
    response = requests.get(url)

    if response:
        response = response.json()
    else:
        console.warning("Genius returned an invalid response. Skipping album check.", label)
        return {}
    # print(url)
    # print(json.dumps(response, indent=4, sort_keys=True))
    
    if len(response.get("response", {}).get("hits", [{}])) == 0:
        console.warning("Genius returned no results. Trying again a single time.", label)
        time.sleep(2)

        url = f'https://{api_base}/search?q={artist} - {song}' # Removing that "-" causes "Kanonenfieber Heizer Tenner" to return a empty result for some reason, even tho it gets an result when looked up via the browser im logged into genius with (although it sometimes returns nothing) May be a temporary server overload https://genius.com/api/search?q=Kanonenfieber%20Heizer%20Tenner
        response = requests.get(url)
        if response:
            response = response.json()
        else:
            console.warning("Genius returned an invalid response. Skipping album check.", label)
            return {}

    if len(response.get("response", {}).get("hits", [{}])) == 0:
        console.warning("Genius returned no results. Continuing without extra Genius album Info", label)
        return {}

    song_api_path = response.get("response", {}).get("hits", [{}])[0].get("result", {}).get("api_path")
    
    #print(json.dumps(response.get("response", {}).get("hits", [{}])[0], indent=4, sort_keys=True))

    url = f'https://{api_base}/{song_api_path}'
    response = requests.get(url)
    if response:
        response = response.json()
    else:
        console.warning("Genius returned an invalid response. Skipping album check.", label)
        return {}

    # --- The genius API lists "album": null sometimes when there is no album. Return false, the song is really a Single (example "Erlkönig - Lūcadelic")
    if not response.get("response", {}).get("song", {}).get("album"):
        return {} # --- Return empty object to avoid .get lookup error on None/False
    
    return {
        "album_name": response.get("response", {}).get("song", {}).get("album", {}).get("name"),
        "artist_name": response.get("response", {}).get("song", {}).get("album", {}).get("artist", {}).get("name"),
        "song_title": response.get("response", {}).get("song", {}).get("title")
    }


    #album_api_path = response.get("response", {}).get("song", {}).get("album", {}).get("api_path")
    #artist_api_path = response.get("response", {}).get("song", {}).get("album", {}).get("artist", {}).get("api_path")
    # url = f'https://api.genius.com/{artist_api_path}'
    # response = requests.get(url, headers=genius_headers).json()
    # print(json.dumps(response, indent=4, sort_keys=True))

