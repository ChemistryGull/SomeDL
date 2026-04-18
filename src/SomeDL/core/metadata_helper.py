import time
import re

from SomeDL.utils.config import config
from SomeDL.utils.utils import clean_song_title, checkIfFileExists
import SomeDL.utils.console as console
from SomeDL.api.genius import geniusGetAlbumBySongName
from SomeDL.api.musicbrainz import musicBrainzGetSongByName, musicBrainzGetArtistByMBID
from SomeDL.api.ytmusic import yt
from SomeDL.api.lrclib import lrclib_get_lyrics
from SomeDL.api.deezer import getDeezerAlbumData
from SomeDL.core.input_parser import parseAlbum

def incr(num: int):
    console.debug("test log")
    return num + 1



# === Main metadata fetching function, calls the downloader ===

def fetch_metadata(metadata, known_metadata: list = []):

    start = time.time()
    console.info(f'Start fetching metadata', metadata.get("label"))

    if checkIfFileExists(metadata["artist_name"], metadata["song_title"], metadata["song_id"]):
        console.info(f'[green]Song does already exist. Skipping download.[/]', metadata.get("label"))

        return "already_downloaded"

    

    # === Guess album ===           time 0.12 or 0.8-2.0
    console.update(metadata.get("label"), "album", console.Status.ACTIVE, "Fetching album data")

    # timerstart("guess_album")
    if not (metadata.get("album_art") and metadata.get("album_artist") and metadata.get("track_pos") and metadata.get("duration")):
        # --- if album data has already been fetched, there is no reason to do a album check as the user has inserted the specific album they wish, so skip it
        console.debug(f'Getting album data from {metadata["album_id"]}', metadata.get("label"))
        album = yt.get_album(metadata["album_id"])

        new_album_id, new_album_name, album = metadata_album_check(metadata["artist_name"], metadata["song_title_clean"], metadata["album_id"], metadata["album_name"], album, label=metadata.get("label"))
        
        metadata["album_id"] = new_album_id
        metadata["album_name"] = new_album_name     

    # === Extract album data from album dict (from YT-API) ===      time < 0.01
        metadata.update(metadata_get_album_data(metadata["song_title"], album))
    
    console.update(metadata.get("label"), "album", console.Status.SUCCESS)

    # timerend("guess_album")

    # === Second check if exists ===
    if checkIfFileExists(metadata["artist_name"], metadata["song_title"], metadata["song_id"], metadata["album_artist"]):
        # --- Second check, neccessary if only album_artist is set
        console.info(f'[green]Song does already exist. Skipping download. (2)[/]', metadata.get("label"))
        return "already_downloaded"

    
    
    # === Get lyrics ===
    metadata.update(metadata_get_lyrics(metadata["artist_name"], metadata["song_title"], metadata.get("duration"), metadata["song_id"], metadata.get("lyrics_id"), metadata.get("label")))


    
    # === Get Genre from MusicBrainz API ===
    # timerstart("musicbrainz")
    metadata.update(metadata_get_genre_mbid(metadata["artist_name"], metadata["album_artist"], metadata["song_title"], known_metadata, metadata.get("label")))
    # timerend("musicbrainz")



    # timerstart("deezer")
    # === Deezer API ====
    metadata.update(metadata_get_label_isrc(metadata["artist_name"], metadata["album_name"], metadata["song_title"], metadata["song_title_clean"], metadata.get("label")))

    # time.sleep(1)
    # return


    # timerend("deezer")


    end = time.time()
    length = end - start
    console.info(f'TIME - The metadata fetching took {length} seconds.', metadata.get("label"))
    metadata["metadata_time"] = length

    return metadata





def metadata_type_cleaner(song_data: dict):
    """
    Takes and modifies existing metadata
    Returns True on success and False on failure
    """

    # === No song id (no valid type) ===
    if not song_data.get("song_id") and not song_data.get("text_query"):
        console.warning(f'Video has no song ID - this might be a regular YouTube video, not a song.', song_data.get("label"))
        console.debug(f'Song ID \"{song_data.get("song_id")}\" is not valid', song_data.get("label"))
        return False

    # === Query ===
    if song_data.get("video_type") == "Search query":
        console.info(f'Looking up song by query', song_data.get("label"))

        query = song_data.get("text_query")

        search_results_query = yt.search(query, filter="songs")

        if len(search_results_query) == 0:
            console.warning(f'Query "{query}" got no results', song_data.get("label"))
            return False

        for i in range(min(len(search_results_query), 3)): # --- Print the first 3 search results 
            console.debug("YT-Result " + str(i) + ": " + search_results_query[i].get("artists")[0].get("name") + " - " + search_results_query[i].get("title", "No title found") + " | " + search_results_query[i].get("album", {}).get("name"), song_data.get("label"))

        search_results = search_results_query[0]

    # === ATV ===
    elif song_data.get("video_type") == "MUSIC_VIDEO_TYPE_ATV" and song_data.get("album_id"):
        console.info(f'Song type is ATV', song_data.get("label"))
        return True # --- Nothing to change if its ATV

    # === OMV ===
    else: # MUSIC_VIDEO_TYPE_OMV (and MUSIC_VIDEO_TYPE_UGC, tho not sure about its functionality)
        console.info("Song type is OMV or other. Looking up based on query", song_data.get("label"))
        
        query = f'{song_data.get("artist_name", None)} - {song_data.get("song_title", None)}'

        search_results_query = yt.search(query, filter="songs")

        if len(search_results_query) == 0:
            console.warning(f'Query "{query}" got no results', song_data.get("label"))
            return False

        for i in range(min(len(search_results_query), 3)): # --- Print the first 3 search results 
            console.debug("YT-Result " + str(i) + ": " + search_results_query[i].get("artists")[0].get("name") + " - " + search_results_query[i].get("title", "No title found") + " | " + search_results_query[i].get("album", {}).get("name"), song_data.get("label"))

        search_results = search_results_query[0]

    if search_results:
        # printj(search_results)
        song_data["album_name"] =        search_results.get("album", {}).get("name")
        song_data["album_id"] =          search_results.get("album", {}).get("id")
        song_data["artist_name"] =       search_results.get("artists", [{}])[0].get("name")
        song_data["artist_id"] =         search_results.get("artists", [{}])[0].get("id")
        song_data["artist_all_names"] =  [a.get("name") for a in search_results.get("artists", [])]
        song_data["song_title"] =        search_results.get("title", "No title found").strip()
        song_data["song_id"] =           search_results.get("videoId", "No title id found")
        song_data["video_type"] =        search_results.get("videoType",  "No video type found") # --- ("MUSIC_VIDEO_TYPE_ATV" - official audio | "MUSIC_VIDEO_TYPE_OMV" - official music video)
        song_data["yt_url"] =            f'https://music.youtube.com/watch?v={song_data["song_id"]}'
        song_data["duration"] =          search_results.get("duration_seconds")
        song_data["song_title_clean"] =  clean_song_title(search_results.get("title"))
        # song_data["song_title_clean"] =  re.sub(r"\(.*?\)", "", song_data["song_title"]).rstrip()
        return True
        
    return False



# === Fetch Albums ===
def fetch_albums(songs_list):
    new_song_list = []
    failed_list = []
    for song in songs_list:
        try:
            # === Clean input ===
            clean_success = metadata_type_cleaner(song)
            if not clean_success:
                failed_list.append(song)
                console.error("Failed to add song from album to download! Skipping...")
                continue

            # === Choose album if present ===
            album = yt.get_album(song["album_id"])
            new_album_id, new_album_name, album = metadata_album_check(song["artist_name"], song["song_title_clean"], song["album_id"], song["album_name"], album)
            song["album_id"] = new_album_id
            song["album_name"] = new_album_name     
            song.update(metadata_get_album_data(song["song_title"], album))

            # === Get album tracks ===
            album_items = parseAlbum(song["album_id"])
            new_song_list.extend(album_items)
            console.info(f'Added Album \"{song["album_name"]}\" to the list.')
        except Exception as e:
            songname = song.get("text_query", f'{song.get("artist_name")} - {song.get("song_title")}')
            console.error(f'Failed to fetch album for \"{songname}\"')
            continue

    return new_song_list, failed_list
            


# === Album Check ===
def metadata_album_check(artist_name: str, song_title: str, album_id: str, album_name: str, album: dict, label: str = None):
    
    console.debug(f'Album type is: {album.get("type", "")}', label)

    if album.get("type") not in ("Single", "EP"):
        console.debug("Album-check: Is album, no check required", label)
        return album_id, album_name, album

    if config["api"]["genius_album_check"] and config["api"]["genius"]:
        console.debug("Album-check: Song is listed as a single. Cross-checking with genius", label)
        console.update(label, "album", console.Status.ACTIVE, "Checking album on genius")
        guessed_album = geniusGetAlbumBySongName(artist_name, song_title, label)
    else:
        console.debug("Album-check: Genius is disabled", label)
        return album_id, album_name, album

    if not guessed_album.get("album_name"):
        console.debug("Album-check: Genius delivered no results", label)
        return album_id, album_name, album

    console.update(label, "album", console.Status.ACTIVE, "Crosschecking genius result with YouTube")
    yt_album_check = yt.search(guessed_album.get("album_name") + " " + artist_name, filter="albums")

    if len(yt_album_check) == 0:
        console.debug("Album-check: YT-search delivered no results", label)
        return album_id, album_name, album

    if yt_album_check[0].get("artists", [{}])[0].get("name") != artist_name:
        console.debug("Album-check: Artists are not the same - aborting album check", label)
        return album_id, album_name, album

    new_album_id = yt_album_check[0].get("browseId")
    new_album_name = yt_album_check[0].get("title")
    console.debug(f'Album-check: Matching: \'{new_album_name}\' instead of \'{album_name}\'', label)
    new_album = yt.get_album(new_album_id)

    if not new_album or not any(song_title.lower() in (track.get("title") or "").lower() for track in new_album.get("tracks", [])):
        # --- Sometimes, Genius tells us this song is in a album, but youtube does not find that song in that album. 
        # --- Use the original album if thats the case. 
        # --- Example: https://www.youtube.com/watch?v=XfMVF-o7g1o
        console.debug(f'Album-check: Song \'{song_title}\' is not in the album \'{new_album_name}\' according to yt-music. Using original album instead.', label)
        return album_id, album_name, album
    
    console.info(f'Album-check: Successfully changed album to {new_album_name} instead of {album_name}', label)
    return new_album_id, new_album_name, new_album 

# === Album Data ===
def metadata_get_album_data(song_title: str, album: dict):
    # --- Loop through all entries in an album to find the index of the one with the correspodning song title
    song_index = 0
    for i, item in enumerate(album.get("tracks", [])):
        if song_title.lower() in item.get("title").lower():
            song_index = i + 1
            break

    if song_index == 0:
        console.warning("Song index is 0, meaning the song was not found in the album!")

    return {
        "track_pos_counted":  song_index, # --- This and the next should always be the same
        "track_pos":          album.get("tracks", [])[song_index - 1].get("trackNumber", -1),
        "track_count":        album.get("trackCount", 0),
        "album_art":          album.get("thumbnails", []),
        "date":               album.get("year", "No date found"),
        "type":               album.get("type", "No type found"),
        "album_artist":       album.get("artists", [{}])[0].get("name"),
        "duration":           album.get("tracks", [])[song_index - 1].get("duration_seconds")
    }


# === Lyrics ===
def metadata_get_lyrics(artist_name: str = None, song_title: str = None, duration: int = None, song_id: str = None, lyrics_id: str = None, label: str = None):
    """
    Return Values:
    {
        lyrics_plain: str,
        lyrics_synced: str,
        instrumental: bool
    }
    """
    console.update(label, "get_lyrics", console.Status.ACTIVE, "Fetching lyrics")

    if not config["metadata"]["lyrics"] or config["metadata"]["lyrics_type"] == "none":
        console.update(label, "get_lyrics", console.Status.SKIPPED)
        return {}


    lyrics = get_lyrics_from(config["metadata"]["lyrics_source"], artist_name, song_title, duration, song_id, lyrics_id, label)

    if lyrics == False:
        return {} # --- Console has been updated from within already
    
    if lyrics.get("instrumental"):
        console.info("Lyrics: Song is instrumental, search finished (1)", label)
        console.update(label, "get_lyrics", console.Status.PART_SUCC)
        return lyrics

    if lyrics.get("lyrics_synced") and config["metadata"]["lyrics_type"] in ("synced", "synced_if_available"):
        console.info("Lyrics: Synced lyrics found, search finished (1)", label)
        console.update(label, "get_lyrics", console.Status.SUCCESS)
        return lyrics

    if lyrics.get("lyrics_plain") and config["metadata"]["lyrics_type"] == "plain":
        console.info("Lyrics: Plain lyrics found, search finished (1)", label)
        console.update(label, "get_lyrics", console.Status.SUCCESS)
        return lyrics

    if lyrics.get("lyrics_synced") and lyrics.get("lyrics_plain"):
        console.info("Lyrics: Plain and Synced lyrics found, search finished (1)", label)
        console.update(label, "get_lyrics", console.Status.SUCCESS)
        return lyrics

    console.update(label, "get_lyrics", console.Status.ACTIVE, f'Trying again from {config["metadata"]["lyrics_source"]}')

    lyrics = get_lyrics_from(config["metadata"]["lyrics_fallback_source"], artist_name, song_title, duration, song_id, lyrics_id, label)


    # === Return just for console logging ===
    if lyrics == False:
        return {} # --- Console has been updated from within already

    if lyrics.get("instrumental"):
        console.info("Lyrics: Song is instrumental (2)", label)
        console.update(label, "get_lyrics", console.Status.PART_SUCC)
        return lyrics

    if config["metadata"]["lyrics_type"] == "synced":
        console.info("Lyrics: No synced lyrics found (2)", label)
        console.update(label, "get_lyrics", console.Status.NOT_FOUND)
        return lyrics

    if lyrics.get("lyrics_plain"):
        console.info("Lyrics: Plain lyrics found, search finished (2)", label)
        console.update(label, "get_lyrics", console.Status.SUCCESS)
        return lyrics
    

    console.info("Lyrics: No lyrics found (2)", label)
    console.update(label, "get_lyrics", console.Status.NOT_FOUND)



    return lyrics

    # Test func:
    # printj(metadata_get_lyrics("Delain", "The Cold", 277, "Bsh5NuCI-pM"))

def get_lyrics_from(source: str, artist_name: str = None, song_title: str = None, duration: int = None, song_id: str = None, lyrics_id: str = None, label: str = None):
    if source.lower() == "none":
        return {}
    if source == "lrclib":
        console.update(label, "get_lyrics", console.Status.ACTIVE, f'Fetching lyrics from lrclib')
        lrclib_lyrics = lrclib_get_lyrics(artist_name, song_title, duration=duration, label=label)
        if lrclib_lyrics == False:
            return False
        return {
            "lyrics_plain": lrclib_lyrics.get("plainLyrics"),
            "lyrics_synced": lrclib_lyrics.get("syncedLyrics"),
            "instrumental": lrclib_lyrics.get("instrumental")
        }
    if source == "youtube":
        console.update(label, "get_lyrics", console.Status.ACTIVE, f'Fetching lyrics from youtube')
        # --- if input is a song URL of type ATV is inserted, lyrics_id was already fetched and is reused, saves time
        if not lyrics_id:
            watch = yt.get_watch_playlist(song_id) # --- This gets the playlist you would see when clicking on a song in yt music. on the top right, there sometimes is a lyrics tab, where it pulls the lyrics from
            lyrics_id = watch.get("lyrics")

        if not lyrics_id:
            console.notice("No lyrics available from the YT-API (no id)", label)
            return {}
        
        yt_lyrics = yt.get_lyrics(lyrics_id)

        if not yt_lyrics:
            return {}

        return {
            "lyrics_plain": yt_lyrics.get("lyrics")
        }

# === Genre, MBID ===
def metadata_get_genre_mbid(artist_name: str, album_artist: str, song_title: str, known_metadata: list, label: str = None):
    """
    Return Values:
    Ideal:      {"mb_artist_mbid", "mb_artist_name", "mb_genres"}

    Optional:   {"mb_failed_timeout"}
    No results: {}

    If previous search got no results, the return values will be empty strings in the dict
      -> {"mb_artist_mbid": "", "mb_artist_name": "", "mb_genres": ""}
    """
    console.update(label, "musicbrainz", console.Status.ACTIVE, "Fetching data from MusicBrainz: MBID")


    # --- Check if artist has already been seen, use this old data if its available
    if not known_metadata == [] and config["api"]["musicbrainz"] and config["metadata"]["genre"]:
        for i, d in enumerate(known_metadata):
            if d.get("artist_name") == artist_name:
                # console.info(artist_name)
                if not d.get("mb_failed_timeout"):
                    # --- If the previous search has already fetched that artist, 
                    # --- and its not empty because of a timeout or error, 
                    # --- Use the data from the previous run
                    console.debug(f'Stayed in "check if artist has already been seen", taking same data; mb_failed_timeout = {d.get("mb_failed_timeout")}', label)
                    console.info(f'Artist {artist_name} MusicBrainz metadata already fetched, skipping API call', label)
                    console.update(label, "musicbrainz", console.Status.SUCCESS)

                    return {
                        "mb_artist_mbid": d.get("mb_artist_mbid", ""),
                        "mb_artist_name": d.get("mb_artist_name", ""),
                        "mb_genres": d.get("mb_genres", "")
                    }
                
                console.debug(f'Continued to the next one in "check if artist has already been seen", getting new data; mb_failed_timeout = {d.get("mb_failed_timeout")}', label)


    # === First get MBID ===

    if not (config["api"]["musicbrainz"] and config["metadata"]["genre"]):
        console.debug("MusicBrainz or genre is disabled", label)
        console.update(label, "musicbrainz", console.Status.SKIPPED)
        return {}

    console.info("Call MusicBrainz API for genre and artist MBID info", label)

    if album_artist.lower() in artist_name.lower():
        # --- If album artist is in artist, its a high chance that the original artist is a feat. or collab in the same artist field.
        # print("Musicbrainz search by album_artist")
        mb_song_res = musicBrainzGetSongByName(album_artist, song_title, label)
    else:
        # --- If album artist is NOT in artist, the album artist is likley not the songs artist (multiple artist collab album)
        # print("Musicbrainz search by song artist_name")
        mb_song_res = musicBrainzGetSongByName(artist_name, song_title, label)

    # print(mb_song_res.get("recordings", [{}]))

    if mb_song_res == None:
        console.notice("Fetching MusicBrainz data failed. Continuing without MusicBrainz metadata (MBID, Genre)", label)
        console.debug("MB Reason for fail: To many retries or other error", label)
        console.update(label, "musicbrainz", console.Status.FAILED)
        return {"mb_failed_timeout": True} # --- Signal that this fail was due to a timeout

    if not len(mb_song_res.get("recordings", [{}])) > 0:
        console.notice("Fetching MusicBrainz data failed. Continuing without MusicBrainz metadata (MBID, Genre)", label)
        console.debug("MB Reason for fail: No artist results", label)
        console.update(label, "musicbrainz", console.Status.NOT_FOUND)
        return {} # --- In the next iteration, use that empty value


    # === With the fetched MBID, get the genre ===

    mb_artist_mbid = mb_song_res.get("recordings", [{}])[0].get("artist-credit", [{}])[0].get("artist", {}).get("id", "")
    mb_artist_name = mb_song_res.get("recordings", [{}])[0].get("artist-credit", [{}])[0].get("name", "")
    
    console.update(label, "musicbrainz", console.Status.ACTIVE, "Fetching data from MusicBrainz: Genre")
    time.sleep(1) # --- Music brainz allows only about 1 request per second. The sleep is not neccessary, but it reduces the retries for the api calls.

    mb_artist = musicBrainzGetArtistByMBID(mb_artist_mbid, label)


    if not mb_artist:
        console.notice("Fetching MusicBrainz artist failed. Continuing without MusicBrainz metadata (Genre)")
        console.debug("MB Reason for fail: To many retries or other error", label)
        console.update(label, "musicbrainz", console.Status.FAILED)
        return {"mb_failed_timeout": True} # --- Signal that this fail was due to a timeout. The only reason this would fail is an error or a timeout. 


    mb_tags = mb_artist.get("tags", False)

    # TODO: Maybe implement that an artist can have multiple genres (user configable, default only one)
    if not mb_tags:
        console.notice("This artist does not have any genre set on MusicBrainz", label)
        console.update(label, "musicbrainz", console.Status.NOT_FOUND)
        return {}

    mb_highest_tag = max(mb_tags, key=lambda x: x["count"])
    mb_genres = mb_highest_tag.get("name", "No MBID genre found")
    console.debug(f'Genre {mb_genres} has been added from MusicBrainz', label)
    console.update(label, "musicbrainz", console.Status.SUCCESS)

    return {
        "mb_artist_mbid": mb_artist_mbid,
        "mb_artist_name": mb_artist_name,
        "mb_genres": mb_genres
    }

# === Label, ISRC ===
def metadata_get_label_isrc(artist_name: str, album_name: str, song_title: str, song_title_clean: str, label):
    console.update(label, "deezer", console.Status.ACTIVE, f'Fetching data from deezer')

    if not (config["api"]["deezer"] and (config["metadata"]["isrc"] or config["metadata"]["copyright"])):
        console.update(label, "deezer", console.Status.SKIPPED)
        console.debug("Fetching data from deezer is disabled", label)
        return {}
    
    deezer_album_data = {}
    try: 
        # deezer_album_data = getDeezerAlbumData(metadata["artist_name"], metadata["album_name"], metadata["song_title"])
        deezer_album_data = getDeezerAlbumData(artist_name, album_name, song_title, label)
        if deezer_album_data == {}:
            # TODO: maybe do not include album in second fetch, and maybe search by album_artist for second fetch?
            
            console.debug("Deezer song search returned no results. Trying with cleaned song title again", label)
            console.update(label, "deezer", console.Status.ACTIVE, f'Fetching data from deezer (Retry)')
            deezer_album_data = getDeezerAlbumData(artist_name, album_name, song_title_clean, label)

    except Exception as e:
        deezer_album_data = {}
        console.error("Failed to fetch album data from Deezer API. No ISRC and label data will be added. Error:", label)
        console.error(e, label)
        console.update(label, "deezer", console.Status.FAILED)
    #print(json.dumps(deezer_album_data, indent=4, sort_keys=True))

    if deezer_album_data == {}:
        console.notice("Deezer API returned no results. Continuing without Deezer metadata (ISRC, Label)", label)
        console.update(label, "deezer", console.Status.NOT_FOUND)
    else:
        console.info("Successfully fetched deezer data", label)
        console.update(label, "deezer", console.Status.SUCCESS)


    return {
        "deezer_genres":        [a.get("name") for a in deezer_album_data.get("genres", {}).get("data", [])],
        "deezer_album_name":    deezer_album_data.get("title", "No deezer album name found"),
        "deezer_album_id":      deezer_album_data.get("id", "No deezer album id found"),
        "deezer_album_label":   deezer_album_data.get("label", None),
        "deezer_artist_name":   deezer_album_data.get("artist", {}).get("name", "No deezer artist name found"),
        "deezer_isrc":          deezer_album_data.get("isrc", "")
    }
