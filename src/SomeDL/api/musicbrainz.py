import requests
import json
import time

from SomeDL.utils.logging import log
from SomeDL.utils.config import config
from SomeDL.utils.version import VERSION

global_retry_counter = 0
musicbrainz_headers = {
    "User-Agent": f"SomeDL/{VERSION} (html.gull@gmail.com)"
}

def musicBrainzGetSongByName(artist: str, song: str):
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
            print("ERROR: Musicbrainz GetSongByName Request failed. No retrying for this Error. Please notify the program maintainer! Error Message: \n", json.dumps(response, indent=4, sort_keys=True))
            return False
        
        global_retry_counter = 0
        return response

    except Exception as e:
        # print("ERROR: Musicbrainz GetSongByName Request failed. Retrying after 5 seconds.", config["global_retry_max"] - global_retry_counter, "attempts left.", e)
        retry_timeout = 5 + global_retry_counter * global_retry_counter
        log.warning(f'Musicbrainz GetSongByName Request failed. Retrying after {retry_timeout} seconds. {config["api"]["max_retry"] - global_retry_counter} attempts left. {e}')
        time.sleep(retry_timeout)
        if global_retry_counter < config["api"]["max_retry"]:
            global_retry_counter = global_retry_counter + 1
            return musicBrainzGetSongByName(artist, song)
    #print(json.dumps(response, indent=4, sort_keys=True))

def musicBrainzGetArtistByMBID(mbid: str,):
    global global_retry_counter
    url = f'https://musicbrainz.org/ws/2/artist/{mbid}?inc=tags&fmt=json'
    try: 
        response = requests.get(url, headers=musicbrainz_headers).json()

        # --- This error should usually not happen. So far have only seen error response when misstyping part of the URL
        if "error" in response:
            print("ERROR: Musicbrainz GetArtistByMBID Request failed. No retrying for this Error. Error Message: \n", json.dumps(response, indent=4, sort_keys=True))
            return False

        global_retry_counter = 0
        return response
    except requests.exceptions.RequestException as e:
        retry_timeout = 5 + global_retry_counter * global_retry_counter
        log.warning(f'Musicbrainz GetArtistByMBID Request failed. Retrying after {retry_timeout} seconds. {config["api"]["max_retry"] - global_retry_counter} attempts left. {e}')
        time.sleep(retry_timeout)
        if global_retry_counter < config["api"]["max_retry"]:
            global_retry_counter = global_retry_counter + 1
            return musicBrainzGetArtistByMBID(mbid)
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

def musicBrainzGetAlbumBySongName(artist: str, song: str, mb_song_res):
    # DEPRECATED!

    # --- START old code guess album part
    # if config["api"]["mb_album_check"] and config["api"]["musicbrainz"] and mb_song_res:
    #         # --- This function should not be used
    #         log.debug("Song is suspected to be listet as a single. Will consult musicbrainz to make a album guess.")
    #         guessed_album = musicBrainzGetAlbumBySongName(metadata["artist_name"], metadata["song_title"], mb_song_res)
    #         #print(guessed_album)
    # --- END old code from guess album part



    mb_release_structure = []



    for recording in mb_song_res.get("recordings", []):
        for release in recording.get("releases", []):
            #print(release.get("release-group", {}).get("title", "No title"))
            item = {
                "title": release.get("release-group", {}).get("title"),
                "primary-type": release.get("release-group", {}).get("primary-type"),
                "secondary-type": release.get("release-group", {}).get("secondary-types"),
            }
            item_str = json.dumps(item, sort_keys=True)

            found = False

            for d in mb_release_structure:
                if d.get("item") == item_str:
                    d["count"] += 1
                    found = True
                    break

            if not found:
                mb_release_structure.append({
                    "item": item_str,
                    "count": 1
                })

    
    mb_release_structure.sort(key=lambda d: d["count"], reverse=True)
    #print(json.dumps(mb_release_structure, indent=4, sort_keys=True))
    album_name = None
    mb_release_type = None
    # --- This just looks for the entry that is most common. As long as this does not have any secondary type (Compilation, live, etc), it is taken.
    # --- Its is not the best way to do this, but since e.g. Sabaton Bismarck has one album entry (which is wrong, it is still just a single, or at best in the Steel commanders Compilation album, but this has a secondary type... its not easy), 
    # --- ... I cannot just get the most frequent album mention. Damn maybe it would indeed be better to consult the Genius API, but this puts it in the steelcommander compilation album.
    # --- ... spotify sees it as a single too, as does youtube (of course)
    # --- this does not work with very popular songs, as it only gets the first couple results and those are mostly trash. e.g. Nirvana smells like teen spirit. But this is only a fallback anyways
    # --- Nirvana example, the correct one does not appear on the first slide: https://musicbrainz.org/search?query=recording%3A%22smells+like+teen+spirit%22+AND+artist%3A%22nirvana%22&type=recording&limit=25&method=advanced&page=1
    # --- The sabaton bismarck case: https://musicbrainz.org/search?query=recording%3A%22Bismarck%22+AND+artist%3A%22sabaton%22&type=recording&limit=25&method=advanced
    for entry in mb_release_structure:
        print(entry)
        entry_dict = json.loads(entry["item"])
        if not entry_dict["secondary-type"]:
            album_name = entry_dict["title"]
            mb_release_type = entry_dict["title"]
            break
    if album_name:
        print("MB Album guess: " + album_name)
    else:
        print("MB found no album name")

    return {"album_name": album_name, "type": mb_release_type}


