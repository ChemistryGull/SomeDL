import requests
import json
import time

import SomeDL.utils.console as console
from SomeDL.utils.config import config
from SomeDL.utils.version import VERSION

global_retry_counter = 0
musicbrainz_headers = {
    "User-Agent": f"SomeDL/{VERSION} (html.gull@gmail.com)"
}

def musicBrainzGetSongByName(artist: str, song: str, label: str = None):
    global global_retry_counter
    if song:
        url = f'https://musicbrainz.org/ws/2/recording/?query=artist:({artist}) AND recording:({song})&fmt=json'
    else: 
        #url = f'https://musicbrainz.org/ws/2/artist/?query={artist}&fmt=json'
        url = f'https://musicbrainz.org/ws/2/recording/?query=artist:"{artist}"&fmt=json'
    try: 
        response = requests.get(url, headers=musicbrainz_headers).json()
        #print(json.dumps(response, indent=4, sort_keys=True))
        # print(url)
        # --- This error should usually not happen. So far have only seen error response when misstyping part of the URL
        if "error" in response:
            if not response.get("error") == "The MusicBrainz web server is currently busy. Please try again later.":
                console.error(f"Musicbrainz GetSongByName Request failed. No retrying for this Error. Please notify the program maintainer! Error Message: \n {json.dumps(response, indent=4, sort_keys=True)}", label)
                return
            else:
                console.warning(f"The MusicBrainz server (genre data) is currently busy! Retrying shortly.", label)
                thime.sleep(2) # Additional 2 seconds of waiting
                raise Exception("MusicBrainz server is busy") # Jump in exception
        
        global_retry_counter = 0
        return response

    except Exception as e:
        # print("ERROR: Musicbrainz GetSongByName Request failed. Retrying after 5 seconds.", config["global_retry_max"] - global_retry_counter, "attempts left.", e)
        retry_timeout = 5 + global_retry_counter * global_retry_counter
        console.notice(f'Musicbrainz GetSongByName Request failed. Retrying after {retry_timeout} seconds. {config["api"]["max_retry"] - global_retry_counter} attempts left. {e}', label)
        console.update(label, "musicbrainz", console.Status.ACTIVE, f'Fetching data from MusicBrainz: MBID (Retry after {retry_timeout} s, {config["api"]["max_retry"] - global_retry_counter} attempts left)')
        time.sleep(retry_timeout)
        if global_retry_counter < config["api"]["max_retry"]:
            global_retry_counter = global_retry_counter + 1
            return musicBrainzGetSongByName(artist, song, label)
    #print(json.dumps(response, indent=4, sort_keys=True))

def musicBrainzGetArtistByMBID(mbid: str, label: str = None):
    global global_retry_counter
    url = f'https://musicbrainz.org/ws/2/artist/{mbid}?inc=tags&fmt=json'
    try: 
        response = requests.get(url, headers=musicbrainz_headers).json()

        # --- This error should usually not happen. So far have only seen error response when misstyping part of the URL
        if "error" in response:
            if not response.get("error") == "The MusicBrainz web server is currently busy. Please try again later.":
                console.error(f"Musicbrainz GetArtistByMBID Request failed. No retrying for this Error. Please notify the program maintainer! Error Message: \n {json.dumps(response, indent=4, sort_keys=True)}", label)
                return
            else:
                console.warning(f"The MusicBrainz server (genre data) is currently busy! Retrying shortly.", label)
                time.sleep(2) # Additional 2 seconds of waiting
                raise Exception("MusicBrainz server is busy") # Jump in exception

        global_retry_counter = 0
        return response
    except requests.exceptions.RequestException as e:
        retry_timeout = 5 + global_retry_counter * global_retry_counter
        console.notice(f'Musicbrainz GetArtistByMBID Request failed. Retrying after {retry_timeout} seconds. {config["api"]["max_retry"] - global_retry_counter} attempts left. {e}', label)
        console.update(label, "musicbrainz", console.Status.ACTIVE, f'Fetching data from MusicBrainz: Genre (Retry after {retry_timeout} s, {config["api"]["max_retry"] - global_retry_counter} attempts left)')
        time.sleep(retry_timeout)
        if global_retry_counter < config["api"]["max_retry"]:
            global_retry_counter = global_retry_counter + 1
            return musicBrainzGetArtistByMBID(mbid, label)
    #print(json.dumps(response, indent=4, sort_keys=True))


def musicBrainzGetSongByMBID(mbid: str,):
    # --- Not used
    url = f'https://musicbrainz.org/ws/2/release/{mbid}?inc=tags&fmt=json'
    response = requests.get(url, headers=musicbrainz_headers).json()
    return response
    #print(json.dumps(response, indent=4, sort_keys=True))

def musicBrainzGetAlbumByMBID(mbid: str,):
    # --- Not used
    url = f'https://musicbrainz.org/ws/2/release-group/{mbid}?inc=tags&fmt=json'
    response = requests.get(url, headers=musicbrainz_headers).json()
    return response
    #print(json.dumps(response, indent=4, sort_keys=True))

