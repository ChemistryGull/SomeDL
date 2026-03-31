import requests
import json

import SomeDL.utils.console as console

def deezerGetSongByQuery(artist: str, album: str, song: str, label: str = None):
    #url = f'https://api.deezer.com/search/?q={query}&index=0&limit=10'
    url = f'https://api.deezer.com/search/?q=artist:"{artist}" album:"{album}" track:"{song}"&index=0&limit=5'
    try:
        response = requests.get(url).json()
        #print(json.dumps(response, indent=4, sort_keys=True))
        return response
    except requests.exceptions.RequestException as e:
        console.error(f'DEEZER API - An error occurred at deezerGetSongByQuery(): {e}', label)
        return False

def deezerGetAlbumByID(id: int, label: str = None):
    url = f'https://api.deezer.com/album/{id}'
    try:
        response = requests.get(url).json()
        return response
    except requests.exceptions.RequestException as e:
        console.error(f'DEEZER API - An error occurred at deezerGetAlbumByID(): {e}', label)
        return False

def getDeezerAlbumData(artist: str, album: str, song: str, label: str = None):
    deezer_album = deezerGetSongByQuery(artist, album, song, label)
    if deezer_album == False:
        return {}

    if "error" in deezer_album:
        console.error("DEEZER API returned error:", label)
        console.error(json.dumps(deezer_album, indent=4, sort_keys=True), label)
        return {}
    
    if deezer_album.get("total") == 0:
        console.debug("DEEZER API returned no results (get song)", label)
        #print(json.dumps(deezer_album, indent=4, sort_keys=True))
        return {}
    # TODO Move these exceptions inside the getDeezerAlbumData functions
    deezer_album_data = deezerGetAlbumByID(deezer_album.get("data", [{}])[0].get("album", {}).get("id", "No album id found"), label)
    if deezer_album_data == False:
        return {}

    if "error" in deezer_album_data:
        console.error("DEEZER API returned error (album data):", label)
        console.error(json.dumps(deezer_album_data, indent=4, sort_keys=True), label)
        return {}
    
    if deezer_album_data.get("total") == 0:
        console.debug("DEEZER API returned no results (album data)", label)
        #print(json.dumps(deezer_album_data, indent=4, sort_keys=True))
        return {}

    #print(json.dumps(deezer_album_data, indent=4, sort_keys=True))

    deezer_album_data["isrc"] = deezer_album.get("data", [{}])[0].get("isrc", "")
    return deezer_album_data



