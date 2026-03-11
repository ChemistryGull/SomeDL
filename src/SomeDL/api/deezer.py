import requests
import json

from SomeDL.utils.logging import log

def deezerGetSongByQuery(artist: str, album: str, song: str):
    #url = f'https://api.deezer.com/search/?q={query}&index=0&limit=10'
    url = f'https://api.deezer.com/search/?q=artist:"{artist}" album:"{album}" track:"{song}"&index=0&limit=5'
    try:
        response = requests.get(url).json()
        #print(json.dumps(response, indent=4, sort_keys=True))
        return response
    except requests.exceptions.RequestException as e:
        print(f'ERROR: DEEZER API - An error occurred at deezerGetSongByQuery(): {e}')
        return False

def deezerGetAlbumByID(id: int):
    url = f'https://api.deezer.com/album/{id}'
    try:
        response = requests.get(url).json()
        return response
    except requests.exceptions.RequestException as e:
        print(f'ERROR: DEEZER API - An error occurred at deezerGetAlbumByID(): {e}')
        return False

def getDeezerAlbumData(artist: str, album: str, song: str):
    deezer_album = deezerGetSongByQuery(artist, album, song)
    if deezer_album == False:
        return {}

    if "error" in deezer_album:
        log.error("DEEZER API returned error:")
        print(json.dumps(deezer_album, indent=4, sort_keys=True))
        return {}
    
    if deezer_album.get("total") == 0:
        log.debug("DEEZER API returned no results (get song)")
        #print(json.dumps(deezer_album, indent=4, sort_keys=True))
        return {}
    # TODO Move these exceptions inside the getDeezerAlbumData functions
    deezer_album_data = deezerGetAlbumByID(deezer_album.get("data", [{}])[0].get("album", {}).get("id", "No album id found"))
    if deezer_album_data == False:
        return {}

    if "error" in deezer_album_data:
        log.error("DEEZER API returned error (album data):")
        print(json.dumps(deezer_album_data, indent=4, sort_keys=True))
        return {}
    
    if deezer_album_data.get("total") == 0:
        log.debug("DEEZER API returned no results (album data)")
        #print(json.dumps(deezer_album_data, indent=4, sort_keys=True))
        return {}

    #print(json.dumps(deezer_album_data, indent=4, sort_keys=True))

    deezer_album_data["isrc"] = deezer_album.get("data", [{}])[0].get("isrc", "")
    return deezer_album_data



