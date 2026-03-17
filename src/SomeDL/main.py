import json
import time
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests

from SomeDL.utils.logging import log, printj, timerstart, timerend
from SomeDL.utils.config import config, load_and_verify_config
from SomeDL.utils.utils import sanitize, generateOutputName, checkIfFileExists
from SomeDL.api.deezer import deezerGetSongByQuery, deezerGetAlbumByID, getDeezerAlbumData
from SomeDL.api.musicbrainz import musicBrainzGetSongByName, musicBrainzGetArtistByMBID
from SomeDL.api.genius import geniusGetAlbumBySongName
from SomeDL.api.ytmusic import yt
from SomeDL.api.lrclib import lrclib_get_lyrics
from SomeDL.core.input_parser import generateSongList
from SomeDL.core.cli_parser import parseCliArgs
from SomeDL.core.downloader import downloadSong
from SomeDL.core.metadata import addMetadata
from SomeDL.core.download_report import generateDownloadReport



def main():
    timer_main = time.time()

    input_args = parseCliArgs()

    if not input_args:
        return

    songs_list = generateSongList(input_args)

    metadata_list, failed_list = processSongList(songs_list)

    if len(songs_list) >= config["logging"]["download_report"]:
        generateDownloadReport(metadata_list, failed_list)
    else:
        log.debug("No Download Report generated")

    end = time.time()
    length = end - timer_main
    if length < 60:
        print(f'TIME - The whole process took {length} seconds.')
    else:
        minutes = length // 60
        seconds = length % 60
        print(f'TIME - The whole process took {round(minutes)} minutes and {round(seconds)} seconds.')



# === Main loop that loops through all songs ===

def processSongList(songs_list):

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
            elif item.get("yt_url") and not config["download"]["always_search_by_query"] and item.get("video_type", None) == "MUSIC_VIDEO_TYPE_ATV":
                log.info("Download by url")
                item_metadata = fetchMetadata(url = item["yt_url"], known_metadata=metadata_list, prefetched_metadata = item)

            elif item.get("text_query", None):
                log.info(f'Download by text query {item.get("text_query", None)}')
                item_metadata = fetchMetadata(query = item["text_query"], known_metadata=metadata_list, prefetched_metadata = item) # --- prefetched_metadata is needed for the original_type = "Search query" to go through

            elif item.get("artist_name", None) and item.get("song_title", None):
                log.info(f'Download based on info: {item.get("artist_name", None)} - {item.get("song_title", None)}')
                item_metadata = fetchMetadata(query = f'{item.get("artist_name", None)} - {item.get("song_title", None)}', known_metadata=metadata_list, prefetched_metadata = item) # --- prefetched_metadata is useless when video_type = OMV (because thei neither return album info nor a lyrics url), but when strictly searching for queries, also ATV videos get here, which do utilze prefetched_metadata

            else:
                print("DEBUG WARNING: uncaught exception happened in getSongList()!!!")

            if item_metadata:
                log.debug("Successfully added Song to metadata list")
                metadata_list.append(item_metadata)
            else:
                log.warning("Song was not downloaded properly (or file does already exist)")
                failed_list.append(item)
        except Exception as e:
            failed_list.append(item)
            log.critical("A critical exception occured when trying to download song with yt-dlp! If retrying does not help, please notify the program maintainer on https://github.com/ChemistryGull/SomeDL. Error: ")
            print(e)
        
        print()

    # print("--- Metadata List ---")
    # print(metadata_list)
    # print("--- Failed List ---")
    # print(failed_list)

    return metadata_list, failed_list


# === Main metadata fetching function, calls the downloader ===

def fetchMetadata(query: str = None, url: str = None, known_metadata: list = [], prefetched_metadata = None):
    # --- Check if input is query or url
    start = time.time()

    # timerstart("Initial_fetch")


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
        metadata["artist_name"] =       search_results.get("artists", [{}])[0].get("name")
        metadata["artist_id"] =         search_results.get("artists", [{}])[0].get("id")
        metadata["artist_all_names"] =  [a.get("name") for a in search_results.get("artists", [])]
        metadata["song_title"] =        search_results.get("title", "No title found")
        # metadata["song_title"] =  re.sub(r"\(.*?\)", "", search_results.get("title", "No title found")).rstrip() # --- Remove mentions like (2020 Remastered). Used to get proper from Musicbrainz and Deezer
        metadata["song_id"] =           search_results.get("videoId", "No title id found")
        metadata["video_type"] =        search_results.get("videoType",  "No video type found") # --- ("MUSIC_VIDEO_TYPE_ATV" - official audio | "MUSIC_VIDEO_TYPE_OMV" - official music video)
        metadata["yt_url"] =            f'https://music.youtube.com/watch?v={metadata["song_id"]}'
        # metadata["duration"] =          search_results.get("duration_seconds")
    # timerend("Initial_fetch")
    # return

    if checkIfFileExists(metadata["artist_name"], metadata["song_title"]):
        log.info(f'\033[32mSong does already exist. Skipping download.\033[32m')
        # --- TODO Add proper return so that the warnig does not appear!!
        return None


    # --- Original url is used when the config option download_url_audio is set to True
    metadata["original_url_id"] = (prefetched_metadata or {}).get("original_url_id")
    
    # --- Remove mentions like (2020 Remastered). Used to get proper from Musicbrainz (TODO: implement in Deezer)
    metadata["song_title_clean"] =  re.sub(r"\(.*?\)", "", metadata["song_title"]).rstrip()

    metadata["original_type"] = (prefetched_metadata or {}).get("original_type")


    #print(json.dumps(metadata, indent=4, sort_keys=True))




    # timerstart("guess_album")

    # === Guess album ===
    album_old = album = yt.get_album(metadata["album_id"])
    album_name_old = metadata["album_name"]
    album_id_old = metadata["album_id"]

    log.debug(f'Album type is: {album.get("type", "")}')
    # --- Check if the song title is the same as the album title. If yes, this may be falsely labels as a single by youtube (it does that quite often).
    # --- Crosscheck with Genius - check that again with yt-dlp
    if (album.get("type", "") == "Single" or album.get("type", "") == "EP"):
        if config["api"]["genius_album_check"] and config["api"]["genius"]:
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
                if album_guess[0].get("artists", [{}])[0].get("name") == metadata["artist_name"]:
                    metadata["zz_OLD_album_name"] = metadata["album_name"]
                    metadata["zz_Genius_album_name_guess"] = album_guess[0].get("title")

                    log.debug(f'Album guess matching: \'{album_guess[0].get("title")}\' instead of \'{metadata["album_name"]}\'')

                    # TODO: these get inevitably overwritten!!!!!!!! Even if the song is not found in the album by youtube!!! 
                    metadata["album_name"] =    album_guess[0].get("title")
                    metadata["album_id"] =      album_guess[0].get("browseId")

                    album = yt.get_album(metadata["album_id"]) # --- get the infos from the newly set album

                else: log.debug("Album-guess: Artists are not the same")
            else: log.debug("Album-guess: YT-search delivered no results")
        else: log.debug("Album-guess: Genius album check delivered no results or are deactivated in the config")
    else:
        log.debug("Album-guess: Entry condition not met")

    # timerend("guess_album")

    # timerstart("get_album_data")

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
        log.debug(f'Song \'{metadata["song_title"]}\' is not in the album \'{metadata["album_name"]}\' according to yt-music. Using original album instead.')

        album = album_old
        metadata["album_name"] = album_name_old
        metadata["album_id"] = album_id_old

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
    metadata["album_artist"] =      album.get("artists", [{}])[0].get("name")
    metadata["duration"] =          album.get("tracks", [])[song_index - 1].get("duration_seconds")



    if checkIfFileExists(metadata["artist_name"], metadata["song_title"], metadata["album_artist"]):
        # --- Second check, neccessary if only album_artist is set
        log.warning(f'Song does already exist. Skipping download. (2)')
        return None


    # timerend("get_album_data")

    # timerstart("get_lyrics")
    #
    # Configs:
    # plain_lyrics
    # synced_lyrics
    # synced_lyrics_with_fallback (different name?)  # --- Use synced lyrics, but use plain lyrics as fallback
    #
    # Sceme:
    # get lrclib
    # if not lrclib
    # get
    #
    # config["metadata"]["plain_lyrics"] or (not metadata["synced_lyrics"] and config["metadata"]["plain_lyrics_fallback"]):
    #

    # config["metadata"]["plain_lyrics"] = True
    # config["metadata"]["synced_lyrics"] = True
    # config["metadata"]["plain_lyrics_fallback"] = True
    # config["api"]["lrclib"] = True
    # config["api"]["youtube_lyrics"] = True
    # # config["metadata"]["lyrics_source"] = "all"

    # if config["api"]["lrclib"]:
    #     lrclib_lyrics = lrclib_get_lyrics(metadata.get("artist_name", ""), metadata.get("song_title"), duration=metadata.get("duration"))
    #     printj(lrclib_lyrics)
    #     metadata["synced_lyrics"] = lrclib_lyrics.get("syncedLyrics")
    #     metadata["plain_lyrics"] = lrclib_lyrics.get("plainLyrics")



    # printj(metadata)
    # return
    # === Get lyrics from YT API ===
    # not config["api"]["lrclib"]

    # yt_fallback_synced = config["metadata"]["plain_lyrics_fallback"] and not metadata.get("synced_lyrics") and not metadata.get("plain_lyrics")
    # yt_fallback_plain = not metadata.get("plain_lyrics")

    # log.debug(f'Got SYNCED lyrics from lrclib: {not metadata["synced_lyrics"] == None}')
    # log.debug(f'Got PLAIN lyrics from lrclib: {not metadata["plain_lyrics"] == None}')
    
    # timerstart("get_lyrics")
    # if config["api"]["youtube_lyrics"] and (yt_fallback_synced or yt_fallback_plain):
    if config["metadata"]["lyrics"]:
        # log.debug("Getting lyrics from youtube api")
        if metadata.get("lyrics_id"): # --- if input is a song URL of type ATV is inserted, this data was already fetched and is reused, saves
            lyrics_id = metadata.get("lyrics_id")
        else:
            watch = yt.get_watch_playlist(metadata["song_id"]) # --- This gets the playlist you would see when clicking on a song in yt music. on the top right, there sometimes is a lyrics tab, where it pulls the lyrics from
            #print(json.dumps(watch, indent=4, sort_keys=True))
            lyrics_id = watch.get("lyrics", False)

        if lyrics_id:
            metadata["lyrics"] = yt.get_lyrics(lyrics_id)
            if metadata["lyrics"]:
                log.info("Got lyrics from the YT-API")
            else:
                log.warning("No lyrics available from the YT-API (no lyrics)")
            #print(json.dumps(lyrics, indent=4, sort_keys=True))
        else:
            metadata["lyrics"] = ""
            log.warning("No lyrics available from the YT-API (no id)")

    # timerend("get_lyrics")



        # === Check if artist has already been seen ===
    # --- (when looking up more than one, avoid unneccessary API calls to musicbrainz)
    # timerstart("check_if_artist_seen")

    artist_seen = None
    if not known_metadata == [] and config["api"]["musicbrainz"] and config["metadata"]["genre"]:
        for i, d in enumerate(known_metadata):
            if d.get("artist_name") == metadata["artist_name"]:
                if (not d.get("mb_artist_mbid") and not config["api"]["mb_retry_artist_name_only"]) or d.get("mb_failed_timeout"):
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

    # timerend("check_if_artist_seen")
    

    # timerstart("musicbrainz")
    # === Get Genre from MusicBrainz API ===
    if config["api"]["musicbrainz"] and config["metadata"]["genre"] and artist_seen == None:
        log.info("Call MusicBrainz API for genre and artist MBID info")
        # TODO: When searching for multiple songs in a row (playlist, multiple queries), check if MBID has already been fetched and use this data instead of making another api call
        if metadata["album_artist"].lower() in metadata["artist_name"].lower():
            # --- If album artist is in artist, its a high chance that the original artist is a feat. or collab in the same artist field.
            # print("Musicbrainz search by album_artist")
            mb_song_res = musicBrainzGetSongByName(metadata["album_artist"], metadata["song_title"])
        else:
            # --- If album artist is NOT in artist, the album artist is likley not the songs artist (multiple artist collab album)
            # print("Musicbrainz search by song artist_name")
            mb_song_res = musicBrainzGetSongByName(metadata["artist_name"], metadata["song_title"])

        #print(json.dumps(mb_song_res, indent=4, sort_keys=True))
        
        if False and mb_song_res and len(mb_song_res.get("recordings", [{}])) == 0 and not metadata["song_title_clean"] == metadata["song_title"].rstrip():
            # --- Musicbrainz may not return songs with names that contain e.g. "(2020 Remastered)" in them. If it found no result before, it will try again with the cleaned query
            log.info("MusicBrainz song search returned no results. Trying with cleaned song title again")
            time.sleep(2)
            mb_song_res = musicBrainzGetSongByName(metadata["artist_name"], metadata["song_title_clean"])
            
        if False and mb_song_res and len(mb_song_res.get("recordings", [{}])) == 0 and config["api"]["mb_retry_artist_name_only"]:
            # --- Musicbrainz did not find that song by that artist. retrying by only searching the artist name. This miht lead to wrong results
            log.warning("MusicBrainz song search returned no results. Trying with artist name only")
            time.sleep(2)
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
                    log.warning("This artist does not have any genre set on MusicBrainz")

            else: 
                log.warning("Fetching MusicBrainz artist failed. Continuing without MusicBrainz metadata (Genre)")
                metadata["mb_failed_timeout"] = True # --- Signal that this fail was due to a timeout. The only reason this would fail is an error or a timeout
        else: 
            log.warning("Fetching MusicBrainz data failed. Continuing without MusicBrainz metadata (MBID, Genre)")
            #print(json.dumps(mb_song_res, indent=4, sort_keys=True))
            if mb_song_res == None:
                metadata["mb_failed_timeout"] = True # --- Signal that this fail was due to a timeout
                log.debug("Reason for fail: To many retries or other error")
            else: 
                log.debug("Reason for fail: No artist results")
    
    # timerend("musicbrainz")


    # timerstart("deezer")
    # === Deezer API ====
    if config["api"]["deezer"] and (config["metadata"]["isrc"] or config["metadata"]["copyright"]):
        try: 
            # deezer_album_data = getDeezerAlbumData(metadata["artist_name"], metadata["album_name"], metadata["song_title"])
            deezer_album_data = getDeezerAlbumData(metadata["artist_name"], metadata["album_name"], metadata["song_title"])
            if deezer_album_data == {}:
                log.debug("Deezer song search returned no results. Trying with cleaned song title again")
                deezer_album_data = getDeezerAlbumData(metadata["artist_name"], metadata["album_name"], metadata["song_title_clean"])
                
                if deezer_album_data == {}:
                    log.warning("DEEZER API returned no results. Continuing without Deezer metadata (ISRC, Label)")
    
        except Exception as e:
            deezer_album_data = {}
            log.error("Failed to fetch album data from Deezer API. No ISRC and label data will be added. Error:")
            print(e)
        #print(json.dumps(deezer_album_data, indent=4, sort_keys=True))
        metadata["deezer_genres"] =         [a.get("name") for a in deezer_album_data.get("genres", {}).get("data", [])]
        metadata["deezer_album_name"] =     deezer_album_data.get("title", "No deezer album name found")
        metadata["deezer_album_id"] =       deezer_album_data.get("id", "No deezer album id found")
        metadata["deezer_album_label"] =    deezer_album_data.get("label", None)
        metadata["deezer_artist_name"] =    deezer_album_data.get("artist", {}).get("name", "No deezer artist name found")
        metadata["deezer_isrc"] =           deezer_album_data.get("isrc", "")



    #print(json.dumps(metadata, indent=4, sort_keys=True))

    log.debug("Youtube: " + metadata["album_name"])
    log.debug("Deezer:  " + metadata.get("deezer_album_name", "-"))
    log.debug("Old YT:  " + metadata.get("zz_OLD_album_name", "-"))
    log.debug("MB:      " + metadata.get("zz_mb_album_name_guess", "-"))
    log.debug("Genius:  " + metadata.get("zz_Genius_album_name_guess", "-"))

    # timerend("deezer")


    end = time.time()
    length = end - start

    if config["download"]["disable_download"]:
        log.warning("Not downloading song as disable-download is set")
        return metadata

    if config["logging"]["level"] == "DEBUG":
        print("TIME - The Metadata fetching took", length, "seconds!")

    if config["download"]["strict_url_download"] and metadata.get("original_url_id"):
        log.info(f'INFO: Downloading audio from original URL as download_url_audio is set: {metadata["original_url_id"]}')
        filename = downloadSong(metadata["original_url_id"], metadata["artist_name"], metadata["album_artist"], metadata["song_title"], metadata["album_name"], metadata["date"], metadata["track_pos"], metadata["track_count"])
    else: 
        filename = downloadSong(metadata["song_id"], metadata["artist_name"], metadata["album_artist"], metadata["song_title"], metadata["album_name"], metadata["date"], metadata["track_pos"], metadata["track_count"])
    if filename:
        addMetadata(metadata, filename)
        metadata["filetype"] = filename.rsplit(".", 1)[-1]
    else: 
        log.error("File was not downloaded successfully with yt-dlp")
        return False


    end = time.time()
    length = end - start
    print("TIME - The song download took", length, "seconds.")
    metadata["download_time"] = f'{round(length, 1)} seconds'

    return metadata





if __name__ == '__main__':
    main()


