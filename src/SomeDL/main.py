from ytmusicapi import YTMusic
import json
import time
import requests
from pathlib import Path
import re
import yt_dlp
#from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, ID3NoHeaderError
#import mutagen
import  mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, USLT, WOAS, WOAR, APIC
from urllib.parse import urlparse, parse_qs
from html import escape
import argparse
import logging
from yt_dlp.utils import DownloadError

VERSION = "0.2.1"

class ColoredFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    # bold_red = "\x1b[31;1m"
    bold_red = "\x1b[1;37;41m"
    reset = "\x1b[0m"
    format = "%(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.basicConfig(
#     level=logging.INFO,
#     # format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
#     format="%(levelname)s | %(name)s | %(message)s"
# )

handler = logging.StreamHandler()
handler.setFormatter(
    ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
)

log.addHandler(handler)





yt = YTMusic()

musicbrainz_headers = {
    "User-Agent": "SomeDL/0.1.1 (html.gull@gmail.com)"
}

global_retry_counter = 0


config = {
    "global_retry_max": 3,
    "lyrics_from_yt": True,
    "get_data_from_musicbrainz": True, # Needed for MBID and Genre
    "mb_album_guess": False, # Requires get_data_from_musicbrainz=true
    "mb_retry_artist_name_only": True,
    "get_data_from_deezer": True, # Needed for label and irsc
    "get_data_from_genius": True,
    "genius_use_official": False, # Default: False - Uses Web API. True requires auth token Please see: https://genius.com/developers
    "genius_token": "",
    #"url_download_mode": "adaptive", # Options: url (CAUSES PROBLEMS - DEPRECATED!! strictly download based on url, may miss metadata), query (always search again by title and artist), adaptive (default - choos query or url based on video type)
    "always_search_by_query": False, # False: default ATV videos will be downloaded via URL. True: All songs get title and artist extractet, and those are searched again
    "download_url_audio": False, # Default False. True: Only uses search by query for metadata, the audio will be downloaded from the original URL regardless
    "disable_download": False, # Default: False; True: only fetch metadata, dont actually downloa, just for Debug
    "download_report_min_inputs": 2 # Default: 2. Minimum number of inputs required to generate download report. Set to a high number to disable download reports
}


def main():
    timer_main = time.time()

    # --- DOC: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="""
Download songs from YouTube by query, multiple queries, or playlist link.

 - Put all inputs in quotes, URLs as well: "Artist - song".
 - Seperate multiple inputs with spaces: "Artist - song" "https://music.youtube..."
 - Different types of URLs and queries can be mixed.
 - Accepted URLs: YT-Music, YT, YT shortended URL, YT playlist. Always include the https://
 - Downloading a full album by album name is not yet supportet""")

    parser.add_argument(
        "inputs",
        nargs="*",  # + One or more inputs | * Zero or more inputs
        help="Song queries (e.g., 'Artist - Song'), YouTube URLs or playlist URLs"
    )
    parser.add_argument(
        "--version",
        action="store_true",  # --- Flag, no value needed
        help="Print version"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",  # --- Flag, no value needed
        help="Verbose output"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",  # --- Flag, no value needed
        help="Silent all info and warning output. Still prints some info and all errors"
    )
    parser.add_argument(
        "--disable-download",
        action="store_true",  # --- Flag, no value needed
        help="Only for debug purposes. Skips the yt-dlp download"
    )
    parser.add_argument(
        "-d", "--download-url-audio",
        action="store_true",  # --- Flag, no value needed
        help="Fetches metadata from youtube search but downloads the audio from the URL."
    )
    parser.add_argument(
        "--cookies-from-browser",
        type=str,
        metavar="BROWSER",
        help="To download age restricted music, use this flag and enter the name of your browser where you are logged into youtube with an age-verified account (e.g. firefox). This flag is passed to yt-dlp. More info: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp"
    )
    parser.add_argument(
        "--cookies",
        type=str,
        metavar="FILEPATH",
        help="Path to cookie file. Only required if you want to download age restricted songs from YouTube and the --cookies-from-browser method does not work (common in chromium based browsers like Chrome or Edge). This flag is passed to yt-dlp. More info: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp"
    )
    parser.add_argument(
        "--no-musicbrainz",
        action="store_true",
        help="Use this flag to skip fetching data from MusicBrainz. No genre data will be added!"
    )
    parser.add_argument(
        "-R","--download-report",
        action="store_true",
        help="Use this flag to generate a download report even if there is only one song input."
    )
    # parser.add_argument(
    #     "--download-folder",
    #     type=str,
    #     default="downloads",  # --- Default folder as string
    #     help="Folder to save downloaded songs"
    # )
    args = parser.parse_args()
    
    if args.verbose:
        log.setLevel(logging.DEBUG)

    if args.quiet:
        log.setLevel(logging.ERROR)

    if args.disable_download:
        config["disable_download"] = True

    if args.download_url_audio:
        config["download_url_audio"] = False

    if args.cookies:
        config["cookies_path"] = args.cookies
    elif args.cookies_from_browser: # --- Only one option is acceptable
        config["cookies_from_browser"] = args.cookies_from_browser


    if args.no_musicbrainz:
        config["get_data_from_musicbrainz"] = False

    if args.download_report:
        config["download_report_min_inputs"] = 1

    check_latest_version(args.version)


    log.debug(f'Inputs: {args.inputs}')
    # print("Set genre:", args.set_genre)
    # print("Download folder:", args.download_folder)

   

    if len(args.inputs) == 0 and args.version:
        return
    elif len(args.inputs) == 0:
        log.info("INFO: No inputs provided")
    else:
        log.debug(f'{len(args.inputs)} inputs provided')
        getSongList(args.inputs)

    end = time.time()
    length = end - timer_main
    print(f'TIME: The whole process took {length} seconds!')



def check_latest_version(print_version):
    # --- Check pypi for latest version
    url = f"https://pypi.org/pypi/somedl/json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        latest_version = data["info"]["version"]
        if not latest_version == VERSION:
            print()
            print(f"SomeDL v{VERSION}. A newer version is available: {latest_version}")
        elif print_version:
            print()
            print(f'SomeDL v{VERSION}. You are up to date.')
        else:
            log.debug(f'SomeDL v{VERSION}. You are up to date.')
    except Exception as e:
        log.warning(f'Could not check PyPI for updates: {e}')




def getSongList(input_list):

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
        
    #print(json.dumps(songs_list, indent=4, sort_keys=True))
    log.debug("Finished input parsing")

    # === Download songs based on input, video type and config ===

    metadata_list = []
    failed_list = []
    
    index = 0
    length = len(songs_list)
    for item in songs_list:
        print("------------------------------------------------------------------------------------------------")
        index += 1
        print(f"Downloading song: {index}/{length}")
        print()
        try: 
            if not item.get("song_id", None) and not item.get("text_query", None):
                # --- Regular videos typically do not show a video ID when in a playlist for some reason. We dont want those anyways, so skip this entry
                log.warning(f'Video "{item.get("song_title", "no name provided"):}" is likely not a song. Skipping')
                failed_list.append(item)
                print()
                continue
            # elif item.get("yt_url", None) and (config["url_download_mode"] == "url" or (item.get("video_type", None) == "MUSIC_VIDEO_TYPE_ATV" and not config["url_download_mode"] == "query")):
            elif item.get("yt_url") and not config["always_search_by_query"] and item.get("video_type", None) == "MUSIC_VIDEO_TYPE_ATV":
                log.info("Download by url")
                item_metadata = getSong(url = item["yt_url"], known_metadata=metadata_list, prefetched_metadata = item)
                
            elif item.get("text_query", None):
                log.info(f'Download by text query {item.get("text_query", None)}')
                item_metadata = getSong(query = item["text_query"], known_metadata=metadata_list, prefetched_metadata = item) # --- prefetched_metadata is needed for the original_type = "Search query" to go through

            elif item.get("artist_name", None) and item.get("song_title", None):
                log.info(f'Download based on info: {item.get("artist_name", None)} - {item.get("song_title", None)}')
                item_metadata = getSong(query = f'{item.get("artist_name", None)} - {item.get("song_title", None)}', known_metadata=metadata_list, prefetched_metadata = item) # --- prefetched_metadata is useless when video_type = OMV (because thei neither return album info nor a lyrics url), but when strictly searching for queries, also ATV videos get here, which do utilze prefetched_metadata
            
            else:
                print("DEBUG WARNING: uncaught exception happened in getSongList()!!!")

            if item_metadata:
                log.debug("Successfully added Song to metadata list")
                metadata_list.append(item_metadata)
            else:
                log.warning("Song was not downloaded properly")
                failed_list.append(item)
        except Exception as e:
            failed_list.append(item)
            log.critical("A critical exception occured when trying to download song with yt-dlp! Please notify the program maintainer on https://github.com/ChemistryGull/SomeDL. Error: ")
            print(e)
        
        print()


    # print("--- Metadata List ---")
    # print(metadata_list)
    # print("--- Failed List ---")
    # print(failed_list)

    if length >= config["download_report_min_inputs"]:
        generateOverviewHTML(metadata_list, failed_list)
    else:
        log.debug("No Download Report generated")

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



# === Main metadata fetching function ===

def getSong(query: str = None, url: str = None, known_metadata: list = [], prefetched_metadata = None):
    # --- Check if input is query or url
    start = time.time()

    # --- If OMW (or UGC) metadata is fetched via URL direchty, ti will not return the album name and id. You will have to look them up manually
    if prefetched_metadata and prefetched_metadata.get("album_name") and prefetched_metadata.get("album_id"):
        # --- Metadata has been prefetched already because the input was a URL
        log.info("Metadata has already been prefetched!")
        metadata = prefetched_metadata
        metadata["query"] = query


    else:
        if url:
            log.info("Looking up song by url")
            parsed_url = urlparse(url)
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
            search_results_url = yt.get_watch_playlist(videoId=video_id, limit=1)

            if len(search_results_url.get("tracks", [])) == 0:
                log.warning(f'Url "{url}" got no results')
                return

            search_results = search_results_url.get("tracks", [{}])[0]
            # TODO: Check if video is: MUSIC_VIDEO_TYPE_OMV or MUSIC_VIDEO_TYPE_UGC. 
            #       Refactor code so that if it only tries to get data if its MUSIC_VIDEO_TYPE_OMV (in a different code block/function) or ask the user if they really want that if its MUSIC_VIDEO_TYPE_UGC
            #       For UGC and most OMV you only get artist and title
            #print(json.dumps(search_results, indent=4, sort_keys=True))
            
        elif query:
            # --- Get songs by looking up query
            log.info("Looking up song by query")
            search_results_query = yt.search(query, filter="songs")
            # print(json.dumps(search_results[0], indent=4, sort_keys=True))
            # return

            if len(search_results_query) == 0:
                log.warning(f'Query "{query}" got no results')
                return

            for i in range(min(len(search_results_query), 3)): # --- Print the first 10 search results 
                log.debug("YT-Result " + str(i) + ": " + search_results_query[i].get("artists")[0].get("name") + " - " + search_results_query[i].get("title", "No title found") + " | " + search_results_query[i].get("album", {}).get("name"))

            search_results = search_results_query[0]

        else:
            log.error("Neither query nor url provided")
            return


        metadata = {"query": query}

        metadata["album_name"] =        search_results.get("album", {}).get("name")
        metadata["album_id"] =          search_results.get("album", {}).get("id")
        metadata["artist_name"] =       search_results.get("artists", [])[0].get("name")
        metadata["artist_id"] =         search_results.get("artists", [])[0].get("id")
        metadata["artist_all_names"] =  [a.get("name") for a in search_results.get("artists", [])]
        metadata["song_title"] =        search_results.get("title", "No title found")
        # metadata["song_title"] =  re.sub(r"\(.*?\)", "", search_results.get("title", "No title found")).rstrip() # --- Remove mentions like (2020 Remastered). Used to get proper from Musicbrainz and Deezer
        metadata["song_id"] =           search_results.get("videoId", "No title id found")
        metadata["video_type"] =        search_results.get("videoType",  "No video type found") # --- ("MUSIC_VIDEO_TYPE_ATV" - official audio | "MUSIC_VIDEO_TYPE_OMV" - official music video)
        metadata["yt_url"] =            f'https://music.youtube.com/watch?v={metadata["song_id"]}'

    new_filename = f'{metadata["artist_name"]} - {metadata["song_title"]}.mp3'
    new_file_path = Path.cwd() / new_filename

    if new_file_path.is_file():
        log.warning(f'Song "{new_filename}" does already exist. Skipping download')
        return None


    # --- Original url is used when the config option download_url_audio is set to True
    metadata["original_url_id"] = (prefetched_metadata or {}).get("original_url_id")
    
    # --- Remove mentions like (2020 Remastered). Used to get proper from Musicbrainz (TODO: implement in Deezer)
    metadata["song_title_clean"] =  re.sub(r"\(.*?\)", "", metadata["song_title"]).rstrip()

    metadata["original_type"] = (prefetched_metadata or {}).get("original_type")


    #print(json.dumps(metadata, indent=4, sort_keys=True))


    # === Check if artist has already been seen ===
    # --- (when looking up more than one, avoid unneccessary API calls)
    artist_seen = None
    if not known_metadata == [] and config.get("get_data_from_musicbrainz"):
        for i, d in enumerate(known_metadata):
            if d.get("artist_name") == metadata["artist_name"]:
                if (not d.get("mb_artist_mbid") and not config.get("mb_retry_artist_name_only")) or d.get("mb_failed_timeout"):
                    # --- If the previous search returned no results for that artist, but it has not searched by artist name only, do not use this old metadata
                    # --- Continue till you find an song that has the metadata, if none is found, the below code will not be executed and it will search for new metadata. 
                    # --- In other words, if mb_retry_artist_name_only is set to true, always reuse the previous search with the 3 lines below 
                    # --- EXCEPT if the fail was because of a timeout (As a search for the same artist will not result in a different result, except if due to a timeout)
                    log.debug(f'Continued to the next one in "check if artist has already been seen", getting new data; mb_failed_timeout = {d.get("mb_failed_timeout")}')
                    continue
                log.debug(f'Stayed in "check if artist has already been seen", taking same data; mb_failed_timeout = {d.get("mb_failed_timeout")}')
                artist_seen = i
                metadata["mb_artist_mbid"] = d.get("mb_artist_mbid", "")
                metadata["mb_artist_name"] = d.get("mb_artist_name", "")
                metadata["mb_genres"] = d.get("mb_genres", "")
                log.info(f'Artist {metadata["artist_name"]} MusicBrainz metadata already fetched, skipping API call')
                break



    # === Get Genre from MusicBrainz API ===
    if config.get("get_data_from_musicbrainz") and artist_seen == None:
        log.info("Call MusicBrainz API for genre and artist MBID info")
        # TODO: When searching for multiple songs in a row (playlist, multiple queries), check if MBID has already been fetched and use this data instead of making another api call
        mb_song_res = musicBrainzGetSongByName(metadata["artist_name"], metadata["song_title"])
        #print(json.dumps(mb_song_res, indent=4, sort_keys=True))

        if mb_song_res and len(mb_song_res.get("recordings", [{}])) == 0:
            # --- Musicbrainz may not return songs with names that contain e.g. "(2020 Remastered)" in them. If it found no result before, it will try again with the cleaned query
            log.info("MusicBrainz song search returned no results. Trying with cleaned song title again")
            time.sleep(2)
            mb_song_res = musicBrainzGetSongByName(metadata["artist_name"], metadata["song_title_clean"])

            if mb_song_res and len(mb_song_res.get("recordings", [{}])) == 0 and config.get("mb_retry_artist_name_only"):
                # --- Musicbrainz did not find that song by that artist. retrying by only searching the artist name. This miht lead to wrong results
                log.info("MusicBrainz song search returned no results. Trying with artist name only")
                time.sleep(3)
                mb_song_res = musicBrainzGetSongByName(metadata["artist_name"], None)

        if mb_song_res and len(mb_song_res.get("recordings", [{}])) > 0:

            metadata["mb_artist_mbid"] = mb_song_res.get("recordings", [{}])[0].get("artist-credit", [{}])[0].get("artist", {}).get("id", "")
            metadata["mb_artist_name"] = mb_song_res.get("recordings", [{}])[0].get("artist-credit", [{}])[0].get("name", "")
            
            time.sleep(1) # --- Music brainz allows only about 1 request per second. The sleep is not neccessary, but it reduces the retries for the api calls.
            mb_artist = musicBrainzGetArtistByMBID(metadata["mb_artist_mbid"])
            #print(json.dumps(mb_artist, indent=4, sort_keys=True))

            if mb_artist:
                mb_tags = mb_artist.get("tags", False)
                #print(json.dumps(mb_tags, indent=4, sort_keys=True))

                # TODO: Implement that an artist can have multiple genres (user configable, default only one)
                if mb_tags:
                    mb_highest_tag = max(mb_tags, key=lambda x: x["count"])
                    metadata["mb_genres"] = mb_highest_tag.get("name", "No MBID genre found")
                    log.debug(f'Genre {metadata["mb_genres"]} has been added from MusicBrainz')
                else:
                    log.warning("MusicBrainz has found no genre")

            else: 
                log.warning("Fetching MusicBrainz artist failed. Continuing without MusicBrainz metadata (Genre)")
                metadata["mb_failed_timeout"] = True # --- Signal that this fail was due to a timeout. The only reason this would fail is an error or a timeout
        else: 
            log.warning("Fetching MusicBrainz song failed. Continuing without MusicBrainz metadata (MBID, Genre)")
            #print(json.dumps(mb_song_res, indent=4, sort_keys=True))
            if mb_song_res == None:
                metadata["mb_failed_timeout"] = True # --- Signal that this fail was due to a timeout
                log.debug("Reason for fail: To many retries or other error")
            else: 
                log.debug("Reason for fail: No results")


    # === Guess album ===
    album_old = album = yt.get_album(metadata["album_id"])

    log.debug(f'Album type is: {album.get("type", "")}')
    # --- Check if the song title is the same as the album title. If yes, this may be falsly labels as a single by youtube (it does that quite often).
    # --- Crosscheck with the desired method (Genius: needs token | MusicBrainz: is probaly inaccurate)
    if (album.get("type", "") == "Single" or album.get("type", "") == "EP"):
        if config["mb_album_guess"] and config["get_data_from_musicbrainz"] and mb_song_res:
            # --- This function should not be used
            log.debug("Song is suspected to be listet as a single. Will consult musicbrainz to make a album guess.")
            guessed_album = musicBrainzGetAlbumBySongName(metadata["artist_name"], metadata["song_title"], mb_song_res)
            #print(guessed_album)
        elif config["get_data_from_genius"]:
            log.debug("Song is suspected to be listet as a single. Will consult Genius official API to make a album guess.")
            guessed_album = geniusGetAlbumBySongName(metadata["artist_name"], metadata["song_title"])
            #print(guessed_album)
        else:
            guessed_album = {}


        if guessed_album.get("album_name"):
            #print("SEARCH QUERY: " + guessed_album["album_name"] + " " + metadata["artist_name"])
            log.debug(f'Album guess found: \'{guessed_album["album_name"]}\'. Checking...')
            album_guess = yt.search(guessed_album["album_name"] + " " + metadata["artist_name"], filter="albums")

            if not len(album_guess) == 0:
                #print(json.dumps(album_guess[0], indent=4, sort_keys=True))

                # --- Check if the artist from the album is still the same as the original one
                #print(album_guess[0].get("artists", [])[0].get("name"), " == ", metadata["artist_name"])
                if album_guess[0].get("artists", [])[0].get("name") == metadata["artist_name"]:
                    metadata["zz_OLD_album_name"] = metadata["album_name"]
                    if config["mb_album_guess"]:
                        metadata["zz_mb_album_name_guess"] = album_guess[0].get("title")
                    elif config["get_data_from_genius"]:
                        metadata["zz_Genius_album_name_guess"] = album_guess[0].get("title")

                    log.debug(f'Album guess matching: \'{album_guess[0].get("title")}\' instead of \'{metadata["album_name"]}\'')

                    # TODO: these get inevitably overwritten!!!!!!!! Even if the song is not found in the album by youtube!!! 
                    metadata["album_name"] =    album_guess[0].get("title")
                    metadata["album_id"] =      album_guess[0].get("browseId")
                    log.debug(f'Found actual album: {metadata["album_name"]}')

                    album = yt.get_album(metadata["album_id"]) # --- get the infos from the newly set album

                else: log.debug("Album-guess: Artists are not the same")
            else: log.debug("Album-guess: YT-search delivered no results")
        else: log.debug("Album-guess: MB-Guess or Genius delivered no results or are deactivated in the config")
    else:
        log.debug("Album-guess: Entry condition not met")



    # === Get album data from YT API ===

    
    #print(json.dumps(album, indent=4, sort_keys=True))
    #return
    # --- Loop through all entries in an album to find the index of the one with the correspodning song title
    song_index = None
    for i, item in enumerate(album.get("tracks", [])):
        #print(item.get("title") + " | " + metadata["song_title"])
        if item.get("title") == metadata["song_title"]:
            song_index = i + 1
            break

    if not song_index:
        # --- Sometimes, Genius tells us this song is in a album, but youtube does not find that song in that album. 
        # --- Search for index in the original album if thats the case. 
        # --- (TODO: Implementing that it forces the cover art of the album found by genius would also be an option to implement)
        # --- Example: https://www.youtube.com/watch?v=XfMVF-o7g1o
        album = album_old
        for i, item in enumerate(album.get("tracks", [])):
            #print(item.get("title") + " | " + metadata["song_title"])
            if item.get("title") == metadata["song_title"]:
                song_index = i + 1
                break

    metadata["track_pos_counted"] = song_index # --- This and the next should always be the same
    metadata["track_pos"] =         album.get("tracks", [])[song_index - 1].get("trackNumber", -1)
    metadata["track_count"] =       album.get("trackCount", 0)
    metadata["album_art"] =         album.get("thumbnails", [])
    metadata["date"] =              album.get("year", "No date found")
    metadata["type"] =              album.get("type", "No type found")



    # === Get lyrics from YT API ===

    if config["lyrics_from_yt"]:
        watch = yt.get_watch_playlist(metadata["song_id"]) # --- This gets the playlist you would see when clicking on a song in yt music. on the top right, there sometimes is a lyrics tab, where it pulls the lyrics from
        # print(json.dumps(watch, indent=4, sort_keys=True))

        lyrics_id = watch.get("lyrics", False)
        if lyrics_id:
            metadata["lyrics"] = yt.get_lyrics(lyrics_id)
            log.info("Got lyrics from the YT-API")
            #print(json.dumps(lyrics, indent=4, sort_keys=True))
        else:
            metadata["lyrics"] = ""
            log.warning("No lyrics available from the YT-API")


    #artist = yt.get_artist(metadata["artist_id"])
    #print(json.dumps(artist, indent=4, sort_keys=True))



    # === Deezer API ====
    if config["get_data_from_deezer"]:
        try: 
            # deezer_album_data = getDeezerAlbumData(metadata["artist_name"], metadata["album_name"], metadata["song_title"])
            deezer_album_data = getDeezerAlbumData(metadata["artist_name"], metadata["album_name"], metadata["song_title"])
            if deezer_album_data == {}:
                log.info("Deezer song search returned no results. Trying with cleaned song title again")
                deezer_album_data = getDeezerAlbumData(metadata["artist_name"], metadata["album_name"], metadata["song_title_clean"])

        except Exception as e:
            deezer_album_data = {}
            log.error("Failed to fetch album data from Deezer API. No genre data will be added. Error:")
            print(e)
        #print(json.dumps(deezer_album_data, indent=4, sort_keys=True))
        metadata["deezer_genres"] =         [a.get("name") for a in deezer_album_data.get("genres", {}).get("data", [])]
        metadata["deezer_album_name"] =     deezer_album_data.get("title", "No deezer album name found")
        metadata["deezer_album_id"] =       deezer_album_data.get("id", "No deezer album id found")
        metadata["deezer_album_label"] =    deezer_album_data.get("label", None)
        metadata["deezer_artist_name"] =    deezer_album_data.get("artist", {}).get("name", "No deezer artist name found")
        metadata["deezer_isrc"] =           deezer_album_data.get("isrc", "")

        # TODO: when implementing multiple song search, test if deezer_album_id has already be seen, if yes, get the data from that entry instead of making a new API call
        # TODO: Maybe add isrc? They would kinda break the above proposed implementation tho


    #print(json.dumps(metadata, indent=4, sort_keys=True))

    log.debug("Youtube: " + metadata["album_name"])
    log.debug("Deezer:  " + metadata.get("deezer_album_name", "-"))
    log.debug("Old YT:  " + metadata.get("zz_OLD_album_name", "-"))
    log.debug("MB:      " + metadata.get("zz_mb_album_name_guess", "-"))
    log.debug("Genius:  " + metadata.get("zz_Genius_album_name_guess", "-"))


    end = time.time()
    length = end - start

    if config.get("disable_download"):
        log.warning("Not downloading song as disable-download is set")
        return metadata

    print("TIME: The Metadata fetching took", length, "seconds!")

    if config["download_url_audio"] and metadata.get("original_url_id"):
        log.info(f'INFO: Downloading audio from original URL as download_url_audio is set: {metadata["original_url_id"]}')
        filename = downloadSong(metadata["original_url_id"], metadata["artist_name"], metadata["song_title"])
    else: 
        filename = downloadSong(metadata["song_id"], metadata["artist_name"], metadata["song_title"])

    if filename:
        addMetadata(metadata, filename)
    else: 
        log.error("File was not downloaded successfully with yt-dlp")
        return False


    end = time.time()
    length = end - start
    print("TIME: The Song download took", length, "seconds!")
    metadata["download_time"] = f'{round(length, 1)} seconds'

    return metadata





def downloadSong(videoID: str, artist: str, song: str): 
    # https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#embedding-yt-dlp. 
    #URLS = ['https://music.youtube.com/watch?v=hComisqDS1I']
    URLS = f'https://music.youtube.com/watch?v={videoID}'
    #URLS = f'https://www.youtube.com/watch?v=-X8Olge799M'
    output_template = f'{artist} - {song}'

    ydl_opts = {
        'format': 'bestaudio/best',
        "remote_components": ["ejs:github"], # --- https://github.com/yt-dlp/yt-dlp/wiki/EJS
        "outtmpl": output_template + '.%(ext)s',
        # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    if config.get("cookies_from_browser"):
        ydl_opts["cookiesfrombrowser"] = (config.get("cookies_from_browser"),) # --- Needs to be a tuple

    if config.get("cookies_path"):
        ydl_opts["cookiefile"] = config.get("cookies_path")

    try: 
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download(URLS)
        return output_template + ".mp3"

    except DownloadError as e:
        log.error(f"yt-dlp download failed. Do you have ffmpeg installed? Is the song {URLS} age restricted?: {e}")
        return False
    except Exception as e:
        log.error(f"Unexpected yt-dlp error: {e}")
        return False
    
    


EasyID3.RegisterTextKey('comment', 'COMM')
EasyID3.RegisterTextKey('audio_source', 'WOAS')

def addMetadata(metadata: str, mp3_file: str):
    #print(json.dumps(metadata, indent=4, sort_keys=True))

    #print(mutagen.File("Delain - Moth to a Flame.mp3").keys())
    
    # dict_keys(['TIT2', 'TPE1', 'TRCK', 'TALB', 'TPOS', 'TDRC', 'TCON', 'POPM:', 'TPE2', 'TSRC', 'TSSE', 'WOAS', 'TENC', 'TCOP', 'COMM::XXX', 'APIC:Cover'])
    # TIT2: Breathe on Me
    # TPE1: Delain
    # TRCK: 1/13
    # TALB: Interlude
    # TPOS: 1/1 TODO (will not be included)
    # TDRC: 2013-08-01
    # TCON: Dutch Metal 
    # POPM:: POPM(email='', rating=58) TODO (Popularimeter, i dont think that needs adding)
    # TPE2: Delain TODO (Album artist)
    # TSRC: ATN261348301
    # TSSE: Lavf58.45.100 TODO (Software/Encoder Settings)
    # TENC: Napalm Records TODO (Encoded by (should be the software like ffmpeg))
    # WOAS: https://open.spotify.com/track/0tGynvJ7MK9hTin02ztQYN
    # TCOP: (C) 2013 Napalm Records Handels GmbH
    # COMM::XXX: https://music.youtube.com/watch?v=sXYPcm3LsLM
    # USLT::XXX: Breathe on me...
    # Breathe on me...

    # A stranger's face that I have never seen
    # But on photographs...
    # ...[Chorus]
    # And call me the wild rose...

    # [Chorus]
    # APIC:Cover: APIC(encoding=<Encoding.UTF16: 1>, mime='image/jpeg', type=<PictureType.COVER_FRONT: 3>, desc='Cover', data=b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x02\x00v\x00v\x00\x00\xff\xdb\x00C\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0c\n\x0c\x0c\x0b\n\x0b\x0b\r\x0e\x12\x10\r\x0e\x11\x0e\x0b\x0b\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14\x18\x12


    # audio = ID3("Delain - Breathe on Me.mp3")

    # # Get all unsynchronised lyrics frames
    # uslt_frames = audio.getall("USLT")
    # print(audio)
    # for frame in uslt_frames:
    #     print("Language:", frame.lang)
    #     print("Description:", frame.desc)
    #     print("Lyrics:\n", frame.text)
    #     print("-" * 40)
    
    # audio = ID3("Delain - Breathe on Me.mp3")
    # for key, value in audio.items():
    #     print(f"{key}: {value}")
    
    # return
    #mp3_file = "I Miss the Misery [hComisqDS1I].mp3"
    # mp3_file = "Invictus (feat. Marko Hietala & Paolo Ribaldini) [3J8VwHPRyN8].mp3"

    if not len(metadata.get("album_art", [{}])) == 0:
        album_art_url = metadata.get("album_art", [{}])[-1].get("url")
        log.debug(f'Album art size: {metadata.get("album_art", [{}])[-1].get("height")} x {metadata.get("album_art", [{}])[-1].get("width")}')
    else:
        album_art_url = None
    
    if album_art_url:
        log.debug("Downloading Album Artwork...")
        album_art_data = downloadAlbumArt(album_art_url)
    else: 
        album_art_data = None


    try:
        tag = EasyID3(mp3_file)
    except:
        tag = mutagen.File(mp3_file, easy=True)
        tag.add_tags()
        log.error("EasyID3 exception occured")

    tag.delete()
    tag['artist'] = metadata.get("artist_name", "")
    tag['title'] = metadata.get("song_title", "")
    tag['date'] = metadata.get("date", "")
    tag['album'] = metadata.get("album_name", "")
    tag['genre'] = metadata.get("mb_genres", "")
    #tag['albumartist'] = 'myalbumartist'
    tag['tracknumber'] = f'{metadata.get("track_pos", "")}/{metadata.get("track_count", "")}'
    #tag['discnumber'] = 'mydiscnumber'
    # tag['audio_source'] = f'https://music.youtube.com/watch?v={metadata.get("song_id", "")}'
    # tag['comment'] = f'https://music.youtube.com/watch?v={metadata.get("song_id", "")}'
    tag['musicbrainz_artistid'] =  metadata.get("mb_artist_mbid", "")
    tag['isrc'] =  metadata.get("deezer_isrc", "")

    if metadata.get("date") and metadata.get("deezer_album_label"):
        tag['copyright'] =  f'{metadata.get("date", "")} {metadata.get("deezer_album_label", "")}'
    else:
        log.debug("Adding no copyright info to metadata no info was found")

    tag.save(v2_version=3)

    #TODO: WOAR = https://www.artistwebsite.com ...oder... WOAR = https://musicbrainz.org/artist/<MBID>
    #TODO: genre: add multiple genres. Seperated by a / on v2.3 (tho not exactly supportet i guess) or a \0 on v2.4. Just a guess to


    # Source: https://stackoverflow.com/questions/42231932/writing-id3-tags-using-easyid3


    id3 = ID3(mp3_file)

    id3.delall("USLT")
    id3.delall("WOAS")
    id3.delall("WOAR")
    id3.delall("APIC")

    if not metadata.get("lyrics") == "":
        id3.add(USLT(
            encoding=3,
            lang = "XXX",
            desc = "",
            text = metadata.get("lyrics", {}).get("lyrics", "")
        ))
    
    id3.add(WOAS(
        url=f'https://music.youtube.com/watch?v={metadata.get("song_id", "")}'
    ))
    # TODO: Add urls to the artist website or the streaming websites. Multiple WOAR tags can be added (appear as "website" on kid3)
    # id3.add(WOAR(
    #     encoding=3,
    #     url='https://music.youtube.com/watch?v=text',
    #     content="xxx"
    # ))

    if album_art_data:
        id3.add(APIC(
            encoding=1,  # (Same as spotdl)
            mime='image/jpeg',  # or 'image/png' depending on the image type
            type=3,  # Cover (front); (same as spotld)
            desc='Cover',
            data=album_art_data
        ))

    id3.save(v2_version=3)



    log.info("Successfully added metadata")

    # print("INFO: Added the following metadata:")
    # audio = ID3(mp3_file)
    # for key, value in audio.items():
    #     print(f"{key}: {value}"[:300])


    return

    mp3_file = "Invictus (feat. Marko Hietala & Paolo Ribaldini) [3J8VwHPRyN8].mp3"

    try:
        audio = ID3(mp3_file)
    except ID3NoHeaderError:
        audio = ID3()

    # Encoding=3 means utf8 (i think)
    audio["TIT2"] = TIT2(encoding=3, text=metadata.get("song_title", ""))
    audio["TPE1"] = TPE1(encoding=3, text=metadata.get("artist_name", "")) # ARTIST
    audio["TALB"] = TALB(encoding=3, text=metadata.get("album_name", "")) # ALBUM
    audio["TRCK"] = TRCK(encoding=3, text="1")
    audio["TCON"] = TCON(encoding=3, text=metadata.get("mb_genres", "")) # GENRE

    #audio["TYER"] = TYER(encoding=3, text="2026") # YEAR ID3v2.3
    #audio["TDRC"] = TDRC(encoding=3, text="2026") # YEAR ID3v2.4

    #audio["COMM"] = TRCK(encoding=3, text="1") # COMMENT
    #audio["TPE2"] = TRCK(encoding=3, text="") # ALBUMARTIST
    #audio["TCOP"] = TRCK(encoding=3, text="") # COPYRIGHT
    #audio["TDAT"] = TDRC(encoding=3, text="2026") # DATE ID3v2.3
    #audio["TXXX:DATE"] = TDRC(encoding=3, text="2026") # DATE ID3v2.4
    #audio["TSRC"] = TRCK(encoding=3, text="") # ISRC
    #audio["TXXX:MusicBrainz Album Artist Id"] = TRCK(encoding=3, text="") # MUSICBRAINZ_ALBUMARTISTID
    #audio["TXXX:MusicBrainz Album Id"] = TRCK(encoding=3, text="") # MUSICBRAINZ_ALBUMID
    #audio["TXXX:MusicBrainz Album Release Country"] = TRCK(encoding=3, text="") # MUSICBRAINZ_ALBUMRELEASECOUNTRY
    #audio["TXXX:MusicBrainz Album Status"] = TRCK(encoding=3, text="") # MUSICBRAINZ_ALBUMSTATUS
    #audio["TXXX:MusicBrainz Album Type"] = TRCK(encoding=3, text="") # MUSICBRAINZ_ALBUMTYPE
    #audio["TXXX:MusicBrainz Artist Id"] = TRCK(encoding=3, text="") # MUSICBRAINZ_ARTISTID
    #audio["TXXX:MusicBrainz Disc Id"] = TRCK(encoding=3, text="") # MUSICBRAINZ_DISCID
    #audio["TXXX:MusicBrainz Original Album Id"] = TRCK(encoding=3, text="") # MUSICBRAINZ_ORIGINALALBUMID
    #audio["TXXX:MusicBrainz Original Artist Id"] = TRCK(encoding=3, text="") # MUSICBRAINZ_ORIGINALARTISTID
    #audio["TXXX:MusicBrainz Release Group Id"] = TRCK(encoding=3, text="") # MUSICBRAINZ_RELEASEGROUPID
    #audio["TXXX:MusicBrainz Release Track Id"] = TRCK(encoding=3, text="") # MUSICBRAINZ_RELEASETRACKID
    #audio["UFID:http://musicbrainz.org"] = TRCK(encoding=3, text="") # MUSICBRAINZ_TRACKID
    #audio["TXXX:MusicBrainz TRM Id"] = TRCK(encoding=3, text="") # MUSICBRAINZ_TRMID
    #audio["TXXX:MusicBrainz Work Id"] = TRCK(encoding=3, text="") # MUSICBRAINZ_WORKID

    #audio["TPUB"] = TRCK(encoding=3, text="") # PUBLISHER
    #audio["USLT"] = TRCK(encoding=3, text="") # UNSYNCEDLYRICS
    #audio[""] = TRCK(encoding=3, text="") # 
    #audio[""] = TRCK(encoding=3, text="") # 
    #audio[""] = TRCK(encoding=3, text="") # 
    #audio[""] = TRCK(encoding=3, text="") # 




    audio.save(mp3_file)
    print("ee")

        

def generateOverviewHTML(data, failed):
    # with open('getPlaylist_data_3.json', 'r') as file:
    #     data = json.load(file)

    #print(json.dumps(data, indent=4, sort_keys=True))

    
    #table = "Oh no..."
    title = "Playlist download report"

    parts = [f'<h1>Download Report {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}</h1>']
    parts.append("<p>Songs that were successfully downloaded:</p>")
    parts.append("<table>")

    relevant_keys = [
        ["Artist", "artist_name"],
        ["Title", "song_title"],
        ["Album", "album_name"],
        ["Date", "date"],
        ["Genre", "mb_genres"],
        ["Track", "track_pos"],
        ["...Of", "track_count"],
        ["Lyrics", "!special"],
        ["Video Type", "original_type"],
        ["URL", "yt_url"],
        ["Albumart", "!special"],
        ["Download time", "download_time"]
    ]

    # Header
    parts.append("<thead><tr>")
    for header in relevant_keys:
        parts.append(f'<th>{escape(str(header[0]))}</th>')
    parts.append("</tr></thead>")

    # Body
    parts.append("<tbody>")
    for item in data:
        parts.append("<tr>")
        for header in relevant_keys:
            if header[1] == "!special":
                match header[0]:
                    case "Lyrics":
                        has_lyrics = not item.get("lyrics", "") == ""
                        if has_lyrics:
                            parts.append(f"<td>Yes</td>")
                        else: 
                            parts.append(f"<td>No</td>")
                    case "Albumart":
                        if not len(item.get("album_art", [{}])) == 0:
                            album_art_url = item.get("album_art", [{}])[-1].get("url")
                            parts.append(f"<td><a target='_blank' href={escape(album_art_url)}>Yes</a></td>")
                        else:
                            parts.append(f"<td>No</td>")

            else:
                parts.append(f'<td>{escape(str(item.get(header[1], "~No data~")))}</td>')
        parts.append("</tr>")
    parts.append("</tbody>")


    parts.append("</table>")
    parts.append("<br>")
    parts.append("<hr>")
    parts.append("<br>")

    parts.append("<p>Songs that failed to download or were already present:</p>")

    parts.append("<table>")

    parts.append("<thead><tr>")
    parts.append("<th>Input Query</th>")
    parts.append("<th>Artist Name</th>")
    parts.append("<th>Song Name</th>")
    parts.append("<th>Video Type</th>")
    parts.append("<th>Youtube URL</th>")

    parts.append("</tr></thead>")

    parts.append("<tbody>")

    for item in failed:
        parts.append("<tr>")
        parts.append(f'<td>{escape(str(item.get("text_query", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("artist_name", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("song_title", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("video_type", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("yt_url", "-")))}</td>')
        parts.append("</tr>")
    parts.append("</tbody>")

    parts.append("</table>")
    
    
    table = "".join(parts)

    html_body = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{escape(title)}</title>
        <style>
            table {{
                border-collapse: collapse;
            }}
            th, td {{
                padding: 8px 12px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .item-failed {{
                background-color: #FF3333;
            }}
        </style>
    </head>
    <body>
    {table}
    </body>
    </html>
    """

    with open(f'Download Report {time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())}.html', "w", encoding="utf-8") as f:
        f.write(html_body)

    log.info("SUCCESS! finished creating HTML overview")





# ==== General API Requests ===



# === Web requests ===
def downloadAlbumArt(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        log.error(" Could not find album art!")
        return False
    
    log.info("Successfully downloaded album art")
    return response.content




# === Genius API ===

genius_headers = {
    "Authorization": f'Bearer {config["genius_token"]}'
}

def geniusGetAlbumBySongName(artist: str, song: str):
    # --- This gets the album name based on an artist and an album query with two API requests at the official Genius API (needs token)
    # TODO: Better error handling! probably crashes the program when problem
    # --- Public API (no auth): https://genius.com/api/
    # --- Official API (auth): https://api.genius.com/
    if config["genius_use_official"]:
        api_base = "api.genius.com"
        g_headers = genius_headers
    else:
        api_base = "genius.com/api"
        g_headers = {}

    url = f'https://{api_base}/search?q={artist} {song}' 
    response = requests.get(url).json()
    # print(url)
    # print(json.dumps(response, indent=4, sort_keys=True))
    
    if len(response.get("response", {}).get("hits", [{}])) == 0:
        print("WARNING: Genius returned no results. Trying again a single time. Its Schrödingers API after all.")
        time.sleep(2)

        url = f'https://{api_base}/search?q={artist} - {song}' # Removing that "-" causes "Kanonenfieber Heizer Tenner" to return a empty result for some reason, even tho it gets an result when looked up via the browser im logged into genius with (although it sometimes returns nothing) May be a temporary server overload https://genius.com/api/search?q=Kanonenfieber%20Heizer%20Tenner
        response = requests.get(url, headers=g_headers).json()
        #print(json.dumps(response, indent=4, sort_keys=True))

    if len(response.get("response", {}).get("hits", [{}])) == 0:
        print("WARNING: Genius returned no results. Continuing without extra Genius album Info")
        return {}

    song_api_path = response.get("response", {}).get("hits", [{}])[0].get("result", {}).get("api_path")
    
    #print(json.dumps(response.get("response", {}).get("hits", [{}])[0], indent=4, sort_keys=True))

    url = f'https://{api_base}/{song_api_path}'
    response = requests.get(url, headers=g_headers).json()
    #print(json.dumps(response, indent=4, sort_keys=True))

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




# === Musicbrainz API ===

def musicBrainzGetSongByName(artist: str, song: str):
    global global_retry_counter
    if song:
        url = f'https://musicbrainz.org/ws/2/recording/?query=artist:"{artist}" AND recording:"{song}"&fmt=json'
    else: 
        url = f'https://musicbrainz.org/ws/2/recording/?query=artist:"{artist}"&fmt=json'
    try: 
        response = requests.get(url, headers=musicbrainz_headers).json()
        #print(json.dumps(response, indent=4, sort_keys=True))
        #print(url)
        # --- This error should usually not happen. So far have only seen error response when misstyping part of the URL
        if "error" in response:
            print("ERROR: Musicbrainz GetSongByName Request failed. No retrying for this Error. Please notify the program maintainer! Error Message: \n", json.dumps(response, indent=4, sort_keys=True))
            return False
        
        global_retry_counter = 0
        return response

    except Exception as e:
        # print("ERROR: Musicbrainz GetSongByName Request failed. Retrying after 5 seconds.", config["global_retry_max"] - global_retry_counter, "attempts left.", e)
        retry_timeout = 5 + global_retry_counter * global_retry_counter
        log.warning(f'Musicbrainz GetSongByName Request failed. Retrying after {retry_timeout} seconds. {config["global_retry_max"] - global_retry_counter} attempts left. {e}')
        time.sleep(retry_timeout)
        if global_retry_counter < config["global_retry_max"]:
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
            print("ERROR: Musicbrainz GetSongByName Request failed. No retrying for this Error. Error Message: \n", json.dumps(response, indent=4, sort_keys=True))
            return False

        global_retry_counter = 0
        return response
    except requests.exceptions.RequestException as e:
        retry_timeout = 5 + global_retry_counter * global_retry_counter
        log.warning(f'Musicbrainz GetArtistByMBID Request failed. Retrying after {retry_timeout} seconds. {config["global_retry_max"] - global_retry_counter} attempts left. {e}')
        time.sleep(retry_timeout)
        if global_retry_counter < config["global_retry_max"]:
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
    #mb_song_res = musicBrainzGetSongByName(artist, song)
    #print(json.dumps(mb_song_res, indent=4, sort_keys=True))

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




# === Deezer API ===


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
        log.warning("DEEZER API returned no results:")
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
        log.warning("DEEZER API returned no results (album data)")
        #print(json.dumps(deezer_album_data, indent=4, sort_keys=True))
        return {}

    #print(json.dumps(deezer_album_data, indent=4, sort_keys=True))

    deezer_album_data["isrc"] = deezer_album.get("data", [{}])[0].get("isrc", "")
    return deezer_album_data





dummy_metadata = {
    "album_art": [
        {
            "height": 60,
            "url": "https://lh3.googleusercontent.com/QTZ68wH7z9K_jOxagJVEgHTG5N9xyb2YMfVITqiceixstw5tXQS6gZHPhZ8-9nUr6OfHOE-bI9Sy0pE=w60-h60-l90-rj",
            "width": 60
        },
        {
            "height": 120,
            "url": "https://lh3.googleusercontent.com/QTZ68wH7z9K_jOxagJVEgHTG5N9xyb2YMfVITqiceixstw5tXQS6gZHPhZ8-9nUr6OfHOE-bI9Sy0pE=w120-h120-l90-rj",
            "width": 120
        },
        {
            "height": 226,
            "url": "https://lh3.googleusercontent.com/QTZ68wH7z9K_jOxagJVEgHTG5N9xyb2YMfVITqiceixstw5tXQS6gZHPhZ8-9nUr6OfHOE-bI9Sy0pE=w226-h226-l90-rj",
            "width": 226
        },
        {
            "height": 544,
            "url": "https://lh3.googleusercontent.com/QTZ68wH7z9K_jOxagJVEgHTG5N9xyb2YMfVITqiceixstw5tXQS6gZHPhZ8-9nUr6OfHOE-bI9Sy0pE=w544-h544-l90-rj",
            "width": 544
        }
    ],
    "album_id": "MPREb_B9YcEZY20ip",
    "album_name": "Dark Waters",
    "artist_all_names": [
        "Delain"
    ],
    "artist_id": "UCPIXyGsEUrGIz7olJ1d7-Ig",
    "artist_name": "Delain",
    "date": "2023",
    "deezer_album_id": 371540297,
    "deezer_album_label": "Napalm Records Handels GmbH",
    "deezer_album_name": "Dark Waters",
    "deezer_artist_name": "Delain",
    "deezer_genres": [
        "Heavy Metal"
    ],
    "deezer_isrc": "ATN262214104",
    "lyrics": {
        "hasTimestamps": False,
        "lyrics": "Deceitful cries under the sun\nTo crucify\nWhat have you done?\nI will not fight your shameful war\nOr spread more lies\nBut I must stand my ground\n\nInvictus I remain\n\nYou're heading towards your own destruction\nYou're heading towards your own destruction\n\nBut what is gained (You mutineers)\nBy a war of pride and greed? (You've made a scene)\nDebris of your failed siege (Now face your empty new frontier - justice)\nWhat you're fighting for you've made a field (You should have learned your end is near)\nOf embers and barbarity (Do you feel it?)\n\nAnd what remains (You mutineers)\nIn the wake of enmity? (You've made a scene)\nDestruction six feet deep (Now face your empty new frontier - justice)\nYou can never take what I've achieved (You should have learned your end is near)\nNev\u0435r, you'll be buried a namel\u0435ss thief (Do you feel it burn?)\n\nWe are now the cruel collective faction\nBow down or face destruction\n\nAnd what remains (You mutineers)\nIn the wake of enmity? (You've made a scene)\nDestruction six feet deep (Now face your empty new frontier - justice)\nYou can never take what I've achieved (You should have learned your end is near)\nNev\u0435r, you'll be buried a namel\u0435ss thief (Do you feel it burn?)\n\nI'm gonna watch your fire burn your eyes\nI'm gonna stand in truth you can't deny\nYou crowned a fool\nNow bear your shame\nI will not condescend\nTo bow before your claim\nNot this time\nThis is your last goodbye\n\nBearing the wounds you've given me\nKnowing they're worth the victory\nHolding, always standing my ground\nGround\nLosing your pride and dignity\nScreaming your rage and treachery\nWaging this war of misery now\nNow\n\nInvictus maneo\nPerge ad victoriam\nUndaunted, in the end\nI'll be standing no more sorrow\nI'm watching far below\nSoaring pride is your downfall\nYour cunning collective\nFierce today but gone tomorrow\n\nInvictus maneo\nPerge ad victoriam\nUndaunted, in the end\nI'll be standing no more sorrow\nI'm watching far below\nSoaring pride is your downfall\nYour cunning collective\nFierce today but gone tomorrow",
        "source": None
    },
    "mb_artist_mbid": "3b0e8f01-3fd9-4104-9532-1e4b526ce562",
    "mb_artist_name": "Delain",
    "mb_genres": "symphonic metal",
    "query": "Delain invictus",
    "song_id": "3J8VwHPRyN8",
    "song_title": "Invictus (feat. Marco Hietala, Paolo Ribaldini & Marko Hietala)",
    "track_count": 21,
    "track_pos": 9,
    "track_pos_counted": 9,
    "type": "Album",
    "video_type": "MUSIC_VIDEO_TYPE_ATV",
    "yt_url": "https://music.youtube.com/watch?v=3J8VwHPRyN8"
}



if __name__ == '__main__':
    main()


#downloadAlbumArt("https://lh3.googleusercontent.com/QTZ68wH7z9K_jOxagJVEgHTG5N9xyb2YMfVITqiceixstw5tXQS6gZHPhZ8-9nUr6OfHOE-bI9Sy0pE=w544-h544-l90-rj")

#getSong("Sabaton - Defence of Moscow")
#getSong("Nirvana smells like teen spirit")
#getSong("Castle rat - wizzard") # It only gets the single version for this one, not the one in the album. The one in the album is a music video anyways, which is bad.
#getSong("In flames trigger") # wrong genre
#getSong("Delain - Moth to a flame") # It only gets the single version for this one too
#getSong("Green day - American idiot") # FIXED: checks on yt if type is album first. Genius makes an "American Idiot (20th Anniversary Deluxe Edition)" out of it sadly. BC of that, deezer does not find anything.
#getSong("Delain invictus")
#getSong("Mushroomhead - Empty Spaces")
#getSong(url="https://music.youtube.com/watch?v=Bsh5NuCI-pM")

#getSong(url="https://www.youtube.com/watch?v=bx9AUS4Titw") # --- Example of non-yt-music song video of type MUSIC_VIDEO_TYPE_OMV. Exceptions have to be made to avoid errors.
#getSong(url="https://www.youtube.com/watch?v=Kyfv-_qMi5Y") # --- Example of normal yt video of type MUSIC_VIDEO_TYPE_UGC. Exceptions have to be made to avoid errors.
#getSong(url="https://www.youtube.com/watch?v=S7LJcjjq6kQ&list=PLZtI2cMRFDYPmT-kL4R-5zf-zL92b2Un_&index=2")
#getSong("TBS - Ü30") # --- Investigate: Genius album guess does not work for this one

#getSong(url="https://music.youtube.com/watch?v=6ZQiyztHzdc")
#getSong("Delain invictus", known_metadata=[dummy_metadata])
#getSong("Delain - Moth to a Flame")



# List of all relevant APIs i found

# Lyrics
# - The yt api itself: Free | No auth | Has most lyrics, but no genre info
# - Musixmatch: Paid only
# - lyrics.ovh: Free | No auth | Only lyrics




# {
#     "album": {
#         "id": "MPREb_LCri5dVbFK2",
#         "name": "2Cellos"
#     },
#     "artists": [
#         {
#             "id": "UCxwLkfMCfx2uSKO9w4iRfDQ",
#             "name": "2CELLOS"
#         },
#         {
#             "id": "UCQAmePE--thWfJkRH7fLOyw",
#             "name": "HAUSER"
#         },
#         {
#             "id": "UCaGmu7iymesYmwLfMB1WnvQ",
#             "name": "Luka Sulic"
#         }
#     ],
#     "category": "Songs",
#     "duration": "2:51",
#     "duration_seconds": 171,
#     "inLibrary": false,
#     "isExplicit": false,
#     "pinnedToListenAgain": false,
#     "resultType": "song",
#     "thumbnails": [
#         {
#             "height": 60,
#             "url": "https://lh3.googleusercontent.com/u1jSf7Tpn2xZLH0Gabp_MftU_f5MYvLxJER0l9ZiOLQYNKUfwtSwNdLrx-Vwfk3wTckUuoWcHdLnPW5U=w60-h60-s-l90-rj",
#             "width": 60
#         },
#         {
#             "height": 120,
#             "url": "https://lh3.googleusercontent.com/u1jSf7Tpn2xZLH0Gabp_MftU_f5MYvLxJER0l9ZiOLQYNKUfwtSwNdLrx-Vwfk3wTckUuoWcHdLnPW5U=w120-h120-s-l90-rj",
#             "width": 120
#         }
#     ],
#     "title": "Smells Like Teen Spirit",
#     "videoId": "Kx1BOUufNo0",
#     "videoType": "MUSIC_VIDEO_TYPE_ATV",
#     "views": "1M",
#     "year": null
# }
