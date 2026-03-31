import json

from urllib.parse import urlparse, parse_qs

import SomeDL.utils.console as console
from SomeDL.utils.config import config
from SomeDL.utils.utils import clean_song_title
from SomeDL.api.ytmusic import yt


def generateSongList(input_list):
    # === Parse all items and create a list first ===
    songs_list = []

    for item in input_list:
        item_parsed = parseInput(item)

        if item_parsed["inp_type"] == "album" and item_parsed.get("album_id", None):
            album = parseAlbum(item_parsed["album_id"])
            if album:
                songs_list.extend(album)
            else:
                console.error(f"Album skipped: {item}")

        elif item_parsed["inp_type"] == "playlist" and item_parsed.get("playlist_id", None):
            playlist = parsePlaylist(item_parsed["playlist_id"])
            if playlist:
                songs_list.extend(playlist)
            else:
                console.error(f"Playlist skipped: {item}")

        elif item_parsed["inp_type"] == "url" and item_parsed.get("video_id", None):
            song = parseSongURL(item_parsed["video_id"])
            if song:
                song["original_url_id"] = item_parsed["video_id"]
                songs_list.append(song)
            else:
                console.error(f"Song skipped: {item}")

        elif item_parsed["inp_type"] == "query":
            songs_list.append({
                "text_query": item,
                "video_type": "Search query",
                "video_type_original": "Search query"
            })

        # --- If none of these types, the input was not valid so it was ignored

    if alert_list_and_v and not config["download"]["prefer_playlist"]:
        # --- To warn the user that only a song will be downloaded. Remove in the future. Also remove the aprt inside the parseInput function
        print("URL contains both song (v=) and playlist (list=) IDs. Only the song is downloaded. To download the entire playlist, add the '--get-playlist' flag or change the 'prefer_playlist' config.")

    console.debug("Finished input parsing")
    return songs_list


alert_list_and_v = False

def parseInput(inp):
    # --- Parses the user input and returns a object based on if its a vidoe url, playlist url or 
    
    out = {}

    parsed_url = urlparse(inp)
    url_queries = parse_qs(parsed_url.query)

    path_parts = [p for p in parsed_url.path.split("/") if p]


    if parsed_url.scheme == "https":
        if len(path_parts) > 1 and path_parts[0] == "browse":
            if path_parts[1].startswith("MPREb_"):
                console.debug(f"Input is browse URL album: {inp}")
                out["inp_type"] = "album"
                out["album_id"] = path_parts[1]
            elif path_parts[1].startswith("RDCLAK"):
                console.debug(f"Input is browse URL playlist: {inp}")
                out["inp_type"] = "playlist"
                out["playlist_id"] = path_parts[1]
            elif path_parts[1].startswith("UC"):
                console.warning(f"Downloading the entire discography of an artist is not yet supported: {inp}")
            else:
                console.warning(f"Input is not a known type of URL: {inp}")
                out["inp_type"] = None

        elif len(path_parts) > 1 and path_parts[0] == "channel":
            console.warning(f"Downloading the entire discography of an artist is not yet supported: {inp}")

        elif not config["download"]["prefer_playlist"] and url_queries.get("v", None):
            # --- If the user does not want to download a full playlist when bot "v" and "list" are in the URL, only download the video
            # --- like https://music.youtube.com/watch?v=MdqaAXrcBv4 or https://www.youtube.com/watch?v=I0WzT0OJ-E0
            console.debug(f"Input is URL: {inp}")
            out["inp_type"] = "url"
            out["video_id"] = url_queries["v"][0]
            if url_queries.get("list", None):
                # --- To warn the user that only a song will be downloaded. Remove in the future
                global alert_list_and_v
                alert_list_and_v = True

        elif url_queries.get("list", None):
            # --- like https://www.youtube.com/watch?v=D44vQCTY4Qw&list=RDGMEM_v2KDBP3d4f8uT-ilrs8fQ
            console.debug(f"Input is Playlist: {inp}")
            out["inp_type"] = "playlist"
            out["playlist_id"] = url_queries["list"][0]

        elif url_queries.get("v", None):
            # --- like https://music.youtube.com/watch?v=MdqaAXrcBv4 or https://www.youtube.com/watch?v=I0WzT0OJ-E0
            console.debug(f"Input is URL: {inp}")
            out["inp_type"] = "url"
            out["video_id"] = url_queries["v"][0]

        elif parsed_url.netloc == "youtu.be":
            # --- like https://youtu.be/I0WzT0OJ-E0?si=miZyWqXVH_IgjkHL
            console.debug(f"Input is shortened URL: {inp}")
            out["inp_type"] = "url"
            out["video_id"] = parsed_url.path.split("/")[1]
        else:
            console.warning(f"Input is not a valid URL: {inp}")
            out["inp_type"] = None
    else:
        # --- like "Spiritbox - Circle with me"
        console.debug(f"Input is query: {inp}")
        out["inp_type"] = "query"
        out["query"] = inp

    return out


def parseAlbum(album_id: str):

    try:
        album_result = yt.get_album(album_id)
    except Exception as e:
        console.error("Album search returned no results. Skipping this album. Error info:")
        print(e)
        return None

    # print()
    # print("album_result")
    # printj(album_result)
    

    try:
        playlist_result = yt.get_playlist(album_result.get("audioPlaylistId"), limit=None)
    except Exception as e:
        console.error("Playlist search returned no results. Skipping this playlist. Error info:")
        print(e)
        return None

    # print()
    # print("playlist_result")
    # printj(playlist_result)
    
    album = []

    # TODO: Add duration, album_artist etc
    # === Extract information from playlist, track by track ===
    for index, item_album in enumerate(album_result.get("tracks", [])):
        item_playlist = playlist_result.get("tracks", [{}])[index]

        if not item_playlist.get("title") == item_album.get("title"):
            console.error(f'While parsing album: {item_playlist.get("title")} and {item_album.get("title")} are not the same!')

        item_data = {
            "album_name":           item_playlist.get("album", {}).get("name"),
            "album_id":             item_playlist.get("album", {}).get("id"),
            "artist_id":            item_playlist.get("artists", [{}])[0].get("id", ""),
            "artist_name":          item_playlist.get("artists", [{}])[0].get("name", ""),
            "artist_all_names":     [a.get("name") for a in item_playlist.get("artists", [])],
            "is_Explicit":          item_playlist.get("isExplicit"),
            "song_title":           item_playlist.get("title"),
            "song_title_clean":     clean_song_title(item_playlist.get("title")),
            "song_id":              item_playlist.get("videoId"),
            "video_type":           item_playlist.get("videoType"),
            "video_type_original":  item_playlist.get("videoType"),
            "yt_url":               f'https://www.youtube.com/watch?v={item_playlist.get("videoId")}',
            "original_url_id":      item_playlist.get("videoId"),

            "track_pos":            item_album.get("trackNumber", -1),
            "track_count":          album_result.get("trackCount", 0),
            "album_art":            album_result.get("thumbnails", []),
            "date":                 album_result.get("year", "No date found"),
            "type":                 "Album", # --- Fake type to avoid album check, the user knows what they want when they input that
            "album_artist":         album_result.get("artists", [{}])[0].get("name"),
            "duration":             item_album.get("duration_seconds")

        }
        if item_data.get("song_id"):
            item_data["original_url_id"] = item_data.get("song_id")

        album.append(item_data)

    return album

def parsePlaylist(playlist_id: str):
    try:
        playlist_result = yt.get_playlist(playlist_id, limit=None)
    except Exception as e:
        console.error("Playlist search returned no results. Skipping this playlist.")
        console.error("Check if the playlist is not private (Change to unlisted or public). Check if the URL is correct.")
        console.error("Error info:")
        console.error(e)
        return None

    #print(json.dumps(playlist_result, indent=4, sort_keys=True))
    
    playlist = []

    # === Extract information from playlist, track by track ===
    for item in playlist_result.get("tracks", []):
        item_data = {
            "album_id":             (item.get("album") or {}).get("id"),
            "album_name":           (item.get("album") or {}).get("name"),
            "artist_id":            item.get("artists", [{}])[0].get("id", ""),
            "artist_name":          item.get("artists", [{}])[0].get("name", ""),
            "artist_all_names":     [a.get("name") for a in item.get("artists", [])],
            "is_Explicit":          item.get("isExplicit"),
            "song_title":           item.get("title"),
            "song_title_clean":     clean_song_title(item.get("title")),
            "song_id":              item.get("videoId"),
            "video_type":           item.get("videoType"),
            "video_type_original":  item.get("videoType"),
            "yt_url":               f'https://www.youtube.com/watch?v={item.get("videoId")}',
            "original_url_id":      item.get("videoId"),
        }
        if item_data.get("song_id"):
            item_data["original_url_id"] = item_data.get("song_id")

        playlist.append(item_data)

    return playlist

def parseSongURL(song_id: str):
    try:
        # song = yt.get_song(song_id)
        result = yt.get_watch_playlist(song_id)
        # printj(result.get("tracks", [None])[0])
        #print(json.dumps(result, indent=4, sort_keys=True))
    except Exception as e:
        console.error("URL search returned no result. Skipping this URL. Error info:")
        print(e)
        return None

    #print(json.dumps(result, indent=4, sort_keys=True))

    # === Extract information from song metadata ===
    song = result.get("tracks", [None])[0]
    # printj(song)
    if song:
        song_data = {
            "album_id":             (song.get("album") or {}).get("id"),
            "album_name":           (song.get("album") or {}).get("name"),
            "artist_id":            song.get("artists", [{}])[0].get("id", ""),
            "artist_name":          song.get("artists", [{}])[0].get("name", ""),
            "artist_all_names":     [a.get("name") for a in song.get("artists", [])],
            "song_title":           song.get("title"),
            "song_title_clean":     clean_song_title(song.get("title")),
            "song_id":              song.get("videoId"),
            "video_type":           song.get("videoType"),
            "video_type_original":  song.get("videoType"),
            "yt_url":               f'https://www.youtube.com/watch?v={song.get("videoId")}',
            "lyrics_id":            result.get("lyrics", None), # --- API only returns lyrics if its of video_type ATV
            "original_url_id":      song.get("videoId"),
        }
        return song_data
    else:
        console.error("URL search results are empty. Skipping this URL")
        return None
