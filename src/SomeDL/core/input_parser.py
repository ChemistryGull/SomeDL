import json

from urllib.parse import urlparse, parse_qs

from SomeDL.utils.logging import log, printj
from SomeDL.utils.config import config
from SomeDL.api.ytmusic import yt


def generateSongList(input_list):
    # === Parse all items and create a list first ===
    songs_list = []

    for item in input_list:
        item_parsed = parseInput(item)

        if item_parsed["inp_type"] == "playlist" and item_parsed.get("playlist_id", None):
            playlist = parsePlaylist(item_parsed["playlist_id"])
            if playlist:
                songs_list.extend(playlist)
            else:
                log.error(f"Playlist skipped: {item}")

        elif item_parsed["inp_type"] == "url" and item_parsed.get("video_id", None):
            song = parseSongURL(item_parsed["video_id"])
            if song:
                song["original_url_id"] = item_parsed["video_id"]
                songs_list.append(song)
            else:
                log.error(f"Song skipped: {item}")

        elif item_parsed["inp_type"] == "query":
            songs_list.append({
                "text_query": item,
                "original_type": "Search query"
            })

        # --- If none of these types, the input was not valid so it was ignored
    log.debug("Finished input parsing")
    return songs_list

def parseInput(inp):
    # --- Parses the user input and returns a object based on if its a vidoe url, playlist url or 
    
    out = {}

    parsed_url = urlparse(inp)
    url_queries = parse_qs(parsed_url.query)

    if parsed_url.scheme == "https":
        if url_queries.get("list", None):
            # --- like https://www.youtube.com/watch?v=D44vQCTY4Qw&list=RDGMEM_v2KDBP3d4f8uT-ilrs8fQ
            log.debug(f"Input is Playlist: {inp}")
            out["inp_type"] = "playlist"
            out["playlist_id"] = url_queries["list"][0]
        elif url_queries.get("v", None):
            # --- like https://music.youtube.com/watch?v=MdqaAXrcBv4 or https://www.youtube.com/watch?v=I0WzT0OJ-E0
            log.debug(f"Input is URL: {inp}")
            out["inp_type"] = "url"
            out["video_id"] = url_queries["v"][0]
        elif parsed_url.netloc == "youtu.be":
            # --- like https://youtu.be/I0WzT0OJ-E0?si=miZyWqXVH_IgjkHL
            log.debug(f"Input is shortened URL: {inp}")
            out["inp_type"] = "url"
            out["video_id"] = parsed_url.path.split("/")[1]
        else:
            log.warning(f"Input is not a valid URL: {inp}")
            out["inp_type"] = None
    else:
        # --- like "Spiritbox - Circle with me"
        log.debug(f"Input is query: {inp}")
        out["inp_type"] = "query"
        out["query"] = inp
    
    return out


def parsePlaylist(playlist_id: str):

    try:
        playlist_result = yt.get_playlist(playlist_id)
    except Exception as e:
        log.error("Playlist search returned no results. Skipping this playlist. Error info:")
        print(e)
        return None

    #print(json.dumps(playlist_result, indent=4, sort_keys=True))
    
    playlist = []

    # === Extract information from playlist, track by track ===
    for item in playlist_result.get("tracks", []):
        item_data = {
            "album_id": (item.get("album") or {}).get("id"),
            "album_name": (item.get("album") or {}).get("name"),
            "artist_id": item.get("artists", [{}])[0].get("id", ""),
            "artist_name": item.get("artists", [{}])[0].get("name", ""),
            "artist_all_names": [a.get("name") for a in item.get("artists", [])],
            "is_Explicit": item.get("isExplicit"),
            "song_title": item.get("title"),
            "song_id": item.get("videoId"),
            "video_type": item.get("videoType"),
            "original_type": item.get("videoType"),
            "yt_url": f'https://www.youtube.com/watch?v={item.get("videoId")}'
        }
        if item_data.get("song_id"):
            item_data["original_url_id"] = item_data.get("song_id")

        playlist.append(item_data)

    return playlist

def parseSongURL(song_id: str):
    try:
        #song = yt.get_song(item_parsed["video_id"])
        result = yt.get_watch_playlist(song_id)
        #print(json.dumps(result, indent=4, sort_keys=True))
    except Exception as e:
        log.error("URL search returned no result. Skipping this URL. Error info:")
        print(e)
        return None

    #print(json.dumps(result, indent=4, sort_keys=True))

    # === Extract information from song metadata ===
    song = result.get("tracks", [None])[0]
    #print(json.dumps(song, indent=4, sort_keys=True))
    if song:
        song_data = {
            "album_id": (song.get("album") or {}).get("id"),
            "album_name": (song.get("album") or {}).get("name"),
            "artist_id": song.get("artists", [{}])[0].get("id", ""),
            "artist_name": song.get("artists", [{}])[0].get("name", ""),
            "artist_all_names": [a.get("name") for a in song.get("artists", [])],
            "song_title": song.get("title"),
            "song_id": song.get("videoId"),
            "video_type": song.get("videoType"),
            "original_type": song.get("videoType"),
            "yt_url": f'https://www.youtube.com/watch?v={song.get("videoId")}',
            "lyrics_id": result.get("lyrics", None) # --- API only returns lyrics if its of video_type ATV
        }
        return song_data
    else:
        log.error("URL search results are empty. Skipping this URL")
        return None
