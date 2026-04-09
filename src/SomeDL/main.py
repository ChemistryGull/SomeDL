import json
import time
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import threading
import queue
import random


from rich.live import Live
from rich.columns import Columns
from rich.align import Align
import requests


from SomeDL.utils.config import config, load_and_verify_config
from SomeDL.utils.utils import sanitize, generateOutputName, checkIfFileExists
import SomeDL.utils.console as console
from SomeDL.utils.console import thread_lock
from SomeDL.utils.version import VERSION
from SomeDL.api.ytmusic import yt
from SomeDL.core.input_parser import generateSongList
from SomeDL.core.cli_parser import parseCliArgs
from SomeDL.core.metadata_helper import fetch_metadata, metadata_type_cleaner, fetch_albums
from SomeDL.core.downloader import downloadSong
from SomeDL.core.metadata import addMetadata
from SomeDL.core.download_report import generateDownloadReport
from SomeDL.core.extra import import_songs, update_storage_template


# from SomeDL.utils.dev_mode import run_with_data_storage


def main():
    # run_with_data_storage(0) # --- ONLY FOR DEBUG
    timer_main = time.time()

    input_args = parseCliArgs()


    # === Special conditions ===
    if not input_args:
        return

    if input_args[0] == "import":
        import_songs()
        return

    if input_args[0] == "new-template":
        update_storage_template()
        return



    # === Fetch albums if needed ===
    songs_list = generateSongList(input_args)
    failed_list_album = []
    if config["download"]["fetch_albums"]:
        songs_list, failed_list_album = fetch_albums(songs_list)


    # === Main Process loop ===
    # metadata_success_list, failed_list, already_downloaded_list = process_song_list_sequential(songs_list)

    print()
    if config["logging"]["log_level"] > 4:
        console.console.print(Columns([
                    f'[bold dark_cyan]  SomeDL version {VERSION}[/]',
                    Align.right(f'[bold dark_cyan] Album | Lyrics | Genre | Copyright | Audio | Album Art | Add Metadata [/]'),
                ], expand=True, ))
    else:
        console.console.print(f'[bold dark_cyan]  SomeDL version {VERSION}[/]')
    
    print()
    metadata_success_list, failed_list, already_downloaded_list = process_song_list_concurrent(songs_list)


    failed_list.extend(failed_list_album)

    # === Download report ===
    if len(songs_list) >= config["logging"]["download_report"]:
        generateDownloadReport(metadata_success_list, failed_list, already_downloaded_list)
    else:
        console.debug("No Download Report generated")

    # === End timer === TODO add full summary of how many downloaded etc
    end = time.time()
    length = end - timer_main
    print()
    if length < 60:
        print(f'Finished - Download time: {length} seconds.')
    else:
        minutes = length // 60
        seconds = length % 60
        print(f'Finished - Download time: {round(minutes)} minutes and {round(seconds)} seconds.')
    print(f'  Successful downloads:  {len(metadata_success_list)}/{len(songs_list)}')
    print(f'  Failed downloads:      {len(failed_list)}/{len(songs_list)}')
    print(f'  Already downloaded:    {len(already_downloaded_list)}/{len(songs_list)}')
    print()

# === Main loop that loops through all songs ===

def process_song_list_sequential(songs_list):

    # === Download songs based on input, video type and config ===

    metadata_list = []
    failed_list = []
    already_downloaded_list = []
    
    index = 0
    length = len(songs_list)
    for item in songs_list:
        print("------------------------------------------------------------------------------------------------")
        index += 1
        print(f"Downloading song: {index}/{length}")
        print()
        # try:
            
        clean_success = metadata_type_cleaner(item)

        if not clean_success:
            failed_list.append(item)

        # === fetch metadata ===
        metadata = fetch_metadata(item, metadata_list)

        if not metadata:
            log.warning("Song was not downloaded properly")
            failed_list.append(item)
            continue
        if metadata == "already_downloaded":
            already_downloaded_list.append(item)
            continue

        # === Download audio ===
        if config["download"]["disable_download"]:
            log.warning("Not downloading song as disable-download is set")
            metadata_list.append(metadata)
            continue

        if config["download"]["strict_url_download"] and metadata.get("original_url_id"):
            log.info(f'INFO: Downloading audio from original URL as download_url_audio is set: {metadata["original_url_id"]}')
            filename = downloadSong(metadata["original_url_id"], metadata["artist_name"], metadata["album_artist"], metadata["song_title"], metadata["album_name"], metadata["date"], metadata["track_pos"], metadata["track_count"])
        else: 
            filename = downloadSong(metadata["song_id"], metadata["artist_name"], metadata["album_artist"], metadata["song_title"], metadata["album_name"], metadata["date"], metadata["track_pos"], metadata["track_count"])
    

        # === Add Metadata ===
        if filename:
            addMetadata(metadata, filename)
            metadata["filetype"] = filename.rsplit(".", 1)[-1]
        else: 
            log.error("File was not downloaded successfully with yt-dlp")
            failed_list.append(item)
            continue


        log.debug("Successfully added Song to metadata list")
        metadata_list.append(metadata)

        # except Exception as e:
        #     failed_list.append(item)
        #     log.critical("A critical exception occured when trying to download song with yt-dlp! If retrying does not help, please notify the program maintainer on https://github.com/ChemistryGull/SomeDL. Error: ")
        #     print(e)

    
        
        print()

    # print("--- Metadata List ---")
    # print(metadata_list)
    # print("--- Failed List ---")
    # print(failed_list)

    return metadata_list, failed_list, already_downloaded_list





def process_song_list_concurrent(songs_list: list):

    # === Shared variables ===

    _DONE = object()
    NUM_DOWNLOADERS = config["download"]["number_downloaders"]
    QUEUE_MAXSIZE = config["download"]["queue_size"]

    download_queue: queue.Queue = queue.Queue(maxsize=QUEUE_MAXSIZE)

    metadata_success_list: list = []
    failed_list: list = []
    already_downloaded_list: list = []


    # === Metadata fetching thread ===
    def thread_fetch_metadata(songs_list):
        metadata_list = []
        
        index = 0
        length = len(songs_list)

        for item in songs_list:
            index += 1

            if item.get("text_query"):
                label = f'{index}/{length} {item.get("text_query")}'
            else:
                label = f'{index}/{length} {item.get("artist_name")} - {item.get("song_title")}'
            item["label"] = label
            
            try:
                
                # === clean metadata ===
                clean_success = metadata_type_cleaner(item)

                if not clean_success:
                    console.warning(f'Song was not downloaded, error on initial lookup.', item["label"])
                    console.finish(item.get("label"), console.Download_status.FAILED)
                    with console.thread_lock:
                        failed_list.append(item)
                    continue

                # === Create the real label after cleaning metadata. ===
                label = f'{index}/{length} {item.get("artist_name")} - {item.get("song_title")}'
                item["label"] = label

                # === Check if the song was already in the queue ===
                # --- (Neccessary for when the same song is input twice, but is not yet downloaded)
                if any(d.get("artist_name") == item.get("artist_name") and d.get("song_title") == item.get("song_title") for d in metadata_list):
                    console.info("This input is a duplicate", item["label"])
                    console.finish(item.get("label"), console.Download_status.ALREADY_DOWNLOADED)

                    with console.thread_lock:
                        already_downloaded_list.append(item)
                    continue


                # === fetch metadata ===
                
                metadata = fetch_metadata(item, metadata_list)

                if not metadata:
                    console.warning("Song was not downloaded properly", item["label"])
                    console.finish(item.get("label"), console.Download_status.FAILED)
                    with console.thread_lock:
                        failed_list.append(item)
                    continue

                if metadata == "already_downloaded":
                    console.finish(item.get("label"), console.Download_status.ALREADY_DOWNLOADED)
                    
                    with console.thread_lock:
                        already_downloaded_list.append(item)
                    continue

                metadata_list.append(metadata) # --- Used for known_metadata

                if config["download"]["disable_download"]:
                    console.update(label, "disable_download", console.Status.SKIPPED)
                    console.notice("Not downloading song as disable-download is set", item["label"])
                    console.finish(label, console.Download_status.DOWNLOAD_DISABLED)

                    with console.thread_lock:
                        metadata_success_list.append(metadata)
                    continue

                console.update(label, "wait_queue", console.Status.ACTIVE, "Queuing for download")

                download_queue.put(metadata) # ---- blocks when queue is full

                console.update(label, "wait_queue", console.Status.ACTIVE, "Queuing for download (in queue)")
                
            except Exception as e:
                console.error("A critical exception occured when fetching the metadata for this song! If retrying does not help, please notify the program maintainer on https://github.com/ChemistryGull/SomeDL. Error:", label)
                console.error(e, label)
                console.finish(label, console.Download_status.FAILED)
                with console.thread_lock:
                    failed_list.append(item)

        for _ in range(NUM_DOWNLOADERS):
            download_queue.put(_DONE)
            



    # === Downloader thread ===
    def thread_downloader(thread_id: int) -> None:
        while True:
            metadata = download_queue.get()
            if metadata is _DONE:
                break
            
            label = None
            try:
                timer_start = time.time()
                label = metadata.get("label")    
                console.update(label, "wait_queue", console.Status.HIDE)

                console.update(label, "downloading", console.Status.ACTIVE, "yt-dlp: Preparing download")

                # === Download audio ===
                if config["download"]["strict_url_download"] and metadata.get("original_url_id"):
                    console.info(f'INFO: Downloading audio from original URL as download_url_audio is set: {metadata["original_url_id"]}', label)
                    filename = downloadSong(metadata["original_url_id"], metadata["artist_name"], metadata["album_artist"], metadata["song_title"], metadata["album_name"], metadata["date"], metadata["track_pos"], metadata["track_count"], label)
                else: 
                    filename = downloadSong(metadata["song_id"], metadata["artist_name"], metadata["album_artist"], metadata["song_title"], metadata["album_name"], metadata["date"], metadata["track_pos"], metadata["track_count"], label)
            

                # === Add Metadata ===
                if filename:
                    console.update(label, "downloading", console.Status.SUCCESS)
                    
                    addMetadata(metadata, filename, label)
                    metadata["filetype"] = filename.rsplit(".", 1)[-1]
                    with console.thread_lock:
                        metadata_success_list.append(metadata)

                    console.finish(label, console.Download_status.SUCCESS)
                else: 
                    console.error("File was not downloaded successfully with yt-dlp", label)
                    console.update(label, "downloading", console.Status.FAILED)
                    console.finish(label, console.Download_status.FAILED)
                    with console.thread_lock:
                        failed_list.append(metadata)
                    continue

                # === Timer ===
                timer_end = time.time()
                length = timer_end - timer_start
                console.info(f'TIME - The download took {length} seconds.', metadata.get("label"))
                metadata["download_time"] = length
                metadata["total_time"] = f'{round(metadata["download_time"] + metadata.get("metadata_time", 0), 1)} seconds' 
                

            except Exception as e:
                console.error("A critical exception occured when trying to download song with yt-dlp! If retrying does not help, please notify the program maintainer on https://github.com/ChemistryGull/SomeDL. Error:", label)
                console.error(e, label)
                console.finish(label, console.Download_status.FAILED)
                with console.thread_lock:
                    failed_list.append(metadata)

            download_queue.task_done()



    with Live(console.make_table(), refresh_per_second=10, transient=True) as live:
        console.init_live(live)

        threads = (
            [threading.Thread(target=thread_fetch_metadata, args=(songs_list,), daemon=True)]
            + [threading.Thread(target=thread_downloader, args=(i + 1,), daemon=True) for i in range(NUM_DOWNLOADERS)]
        )
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        console.clear_live(live)

    
    return metadata_success_list, failed_list, already_downloaded_list


test_song_list = [
    {
        "album_art": [
            {
                "height": 60,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w60-h60-l90-rj",
                "width": 60
            },
            {
                "height": 120,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w120-h120-l90-rj",
                "width": 120
            },
            {
                "height": 226,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w226-h226-l90-rj",
                "width": 226
            },
            {
                "height": 544,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w544-h544-l90-rj",
                "width": 544
            }
        ],
        "album_artist": "Castle Rat",
        "album_id": "MPREb_zw0AuvoXPdK",
        "album_name": "Into The Realm",
        "artist_all_names": [
            "Castle Rat"
        ],
        "artist_id": "UCWmuYXWWkI1cOJ3GEmrNsig",
        "artist_name": "Castle Rat",
        "date": "2024",
        "duration": 243,
        "is_Explicit": False,
        "original_url_id": "pn-DcNvuJ3w",
        "song_id": "pn-DcNvuJ3w",
        "song_title": "Dagger Dragger",
        "song_title_clean": "Dagger Dragger",
        "track_count": 9,
        "track_pos": 1,
        "type": "Album",
        "video_type": "MUSIC_VIDEO_TYPE_ATV",
        "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
        "yt_url": "https://www.youtube.com/watch?v=pn-DcNvuJ3w"
    },
    {
        "album_art": [
            {
                "height": 60,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w60-h60-l90-rj",
                "width": 60
            },
            {
                "height": 120,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w120-h120-l90-rj",
                "width": 120
            },
            {
                "height": 226,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w226-h226-l90-rj",
                "width": 226
            },
            {
                "height": 544,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w544-h544-l90-rj",
                "width": 544
            }
        ],
        "album_artist": "Castle Rat",
        "album_id": "MPREb_zw0AuvoXPdK",
        "album_name": "Into The Realm",
        "artist_all_names": [
            "Castle Rat"
        ],
        "artist_id": "UCWmuYXWWkI1cOJ3GEmrNsig",
        "artist_name": "Castle Rat",
        "date": "2024",
        "duration": 272,
        "is_Explicit": False,
        "original_url_id": "KWz61oHfR8g",
        "song_id": "KWz61oHfR8g",
        "song_title": "Feed The Dream",
        "song_title_clean": "Feed The Dream",
        "track_count": 9,
        "track_pos": 2,
        "type": "Album",
        "video_type": "MUSIC_VIDEO_TYPE_ATV",
        "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
        "yt_url": "https://www.youtube.com/watch?v=KWz61oHfR8g"
    },
    {
        "album_art": [
            {
                "height": 60,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w60-h60-l90-rj",
                "width": 60
            },
            {
                "height": 120,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w120-h120-l90-rj",
                "width": 120
            },
            {
                "height": 226,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w226-h226-l90-rj",
                "width": 226
            },
            {
                "height": 544,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w544-h544-l90-rj",
                "width": 544
            }
        ],
        "album_artist": "Castle Rat",
        "album_id": "MPREb_zw0AuvoXPdK",
        "album_name": "Into The Realm",
        "artist_all_names": [
            "Castle Rat"
        ],
        "artist_id": "UCWmuYXWWkI1cOJ3GEmrNsig",
        "artist_name": "Castle Rat",
        "date": "2024",
        "duration": 65,
        "is_Explicit": False,
        "original_url_id": "n-a4M6Bhz3s",
        "song_id": "n-a4M6Bhz3s",
        "song_title": "Resurrector",
        "song_title_clean": "Resurrector",
        "track_count": 9,
        "track_pos": 3,
        "type": "Album",
        "video_type": "MUSIC_VIDEO_TYPE_ATV",
        "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
        "yt_url": "https://www.youtube.com/watch?v=n-a4M6Bhz3s"
    },
    {
        "album_art": [
            {
                "height": 60,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w60-h60-l90-rj",
                "width": 60
            },
            {
                "height": 120,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w120-h120-l90-rj",
                "width": 120
            },
            {
                "height": 226,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w226-h226-l90-rj",
                "width": 226
            },
            {
                "height": 544,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w544-h544-l90-rj",
                "width": 544
            }
        ],
        "album_artist": "Castle Rat",
        "album_id": "MPREb_zw0AuvoXPdK",
        "album_name": "Into The Realm",
        "artist_all_names": [
            "Castle Rat"
        ],
        "artist_id": "UCWmuYXWWkI1cOJ3GEmrNsig",
        "artist_name": "Castle Rat",
        "date": "2024",
        "duration": 409,
        "is_Explicit": False,
        "original_url_id": "Kyg4OpZ7vKk",
        "song_id": "Kyg4OpZ7vKk",
        "song_title": "Red Sands",
        "song_title_clean": "Red Sands",
        "track_count": 9,
        "track_pos": 4,
        "type": "Album",
        "video_type": "MUSIC_VIDEO_TYPE_ATV",
        "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
        "yt_url": "https://www.youtube.com/watch?v=Kyg4OpZ7vKk"
    },
    {
        "album_art": [
            {
                "height": 60,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w60-h60-l90-rj",
                "width": 60
            },
            {
                "height": 120,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w120-h120-l90-rj",
                "width": 120
            },
            {
                "height": 226,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w226-h226-l90-rj",
                "width": 226
            },
            {
                "height": 544,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w544-h544-l90-rj",
                "width": 544
            }
        ],
        "album_artist": "Castle Rat",
        "album_id": "MPREb_zw0AuvoXPdK",
        "album_name": "Into The Realm",
        "artist_all_names": [
            "Castle Rat"
        ],
        "artist_id": "UCWmuYXWWkI1cOJ3GEmrNsig",
        "artist_name": "Castle Rat",
        "date": "2024",
        "duration": 76,
        "is_Explicit": False,
        "original_url_id": "jWabKBVKi3A",
        "song_id": "jWabKBVKi3A",
        "song_title": "The Mirror",
        "song_title_clean": "The Mirror",
        "track_count": 9,
        "track_pos": 5,
        "type": "Album",
        "video_type": "MUSIC_VIDEO_TYPE_ATV",
        "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
        "yt_url": "https://www.youtube.com/watch?v=jWabKBVKi3A"
    },
    {
        "album_art": [
            {
                "height": 60,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w60-h60-l90-rj",
                "width": 60
            },
            {
                "height": 120,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w120-h120-l90-rj",
                "width": 120
            },
            {
                "height": 226,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w226-h226-l90-rj",
                "width": 226
            },
            {
                "height": 544,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w544-h544-l90-rj",
                "width": 544
            }
        ],
        "album_artist": "Castle Rat",
        "album_id": "MPREb_zw0AuvoXPdK",
        "album_name": "Into The Realm",
        "artist_all_names": [
            "Castle Rat"
        ],
        "artist_id": "UCWmuYXWWkI1cOJ3GEmrNsig",
        "artist_name": "Castle Rat",
        "date": "2024",
        "duration": 291,
        "is_Explicit": False,
        "original_url_id": "uy9QUYbBKdE",
        "song_id": "uy9QUYbBKdE",
        "song_title": "Cry For Me",
        "song_title_clean": "Cry For Me",
        "track_count": 9,
        "track_pos": 6,
        "type": "Album",
        "video_type": "MUSIC_VIDEO_TYPE_ATV",
        "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
        "yt_url": "https://www.youtube.com/watch?v=uy9QUYbBKdE"
    },
    {
        "album_art": [
            {
                "height": 60,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w60-h60-l90-rj",
                "width": 60
            },
            {
                "height": 120,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w120-h120-l90-rj",
                "width": 120
            },
            {
                "height": 226,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w226-h226-l90-rj",
                "width": 226
            },
            {
                "height": 544,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w544-h544-l90-rj",
                "width": 544
            }
        ],
        "album_artist": "Castle Rat",
        "album_id": "MPREb_zw0AuvoXPdK",
        "album_name": "Into The Realm",
        "artist_all_names": [
            "Castle Rat"
        ],
        "artist_id": "UCWmuYXWWkI1cOJ3GEmrNsig",
        "artist_name": "Castle Rat",
        "date": "2024",
        "duration": 50,
        "is_Explicit": False,
        "original_url_id": "tx3FRlt9gnc",
        "song_id": "tx3FRlt9gnc",
        "song_title": "Realm",
        "song_title_clean": "Realm",
        "track_count": 9,
        "track_pos": 7,
        "type": "Album",
        "video_type": "MUSIC_VIDEO_TYPE_ATV",
        "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
        "yt_url": "https://www.youtube.com/watch?v=tx3FRlt9gnc"
    },
    {
        "album_art": [
            {
                "height": 60,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w60-h60-l90-rj",
                "width": 60
            },
            {
                "height": 120,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w120-h120-l90-rj",
                "width": 120
            },
            {
                "height": 226,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w226-h226-l90-rj",
                "width": 226
            },
            {
                "height": 544,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w544-h544-l90-rj",
                "width": 544
            }
        ],
        "album_artist": "Castle Rat",
        "album_id": "MPREb_zw0AuvoXPdK",
        "album_name": "Into The Realm",
        "artist_all_names": [
            "Castle Rat"
        ],
        "artist_id": "UCWmuYXWWkI1cOJ3GEmrNsig",
        "artist_name": "Castle Rat",
        "date": "2024",
        "duration": 223,
        "is_Explicit": False,
        "original_url_id": "m9YVwSZyufA",
        "song_id": "m9YVwSZyufA",
        "song_title": "Fresh Fur",
        "song_title_clean": "Fresh Fur",
        "track_count": 9,
        "track_pos": 8,
        "type": "Album",
        "video_type": "MUSIC_VIDEO_TYPE_ATV",
        "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
        "yt_url": "https://www.youtube.com/watch?v=m9YVwSZyufA"
    },
    {
        "album_art": [
            {
                "height": 60,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w60-h60-l90-rj",
                "width": 60
            },
            {
                "height": 120,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w120-h120-l90-rj",
                "width": 120
            },
            {
                "height": 226,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w226-h226-l90-rj",
                "width": 226
            },
            {
                "height": 544,
                "url": "https://lh3.googleusercontent.com/S8pGU_GHZlyzQb5CnwshW9MtEUfgWhUIjsliHKC7yiwrEUfHX9rv9wVRcCQK9B369jeruYuROzAMGA0=w544-h544-l90-rj",
                "width": 544
            }
        ],
        "album_artist": "Castle Rat",
        "album_id": "MPREb_zw0AuvoXPdK",
        "album_name": "Into The Realm",
        "artist_all_names": [
            "Castle Rat"
        ],
        "artist_id": "UCWmuYXWWkI1cOJ3GEmrNsig",
        "artist_name": "Castle Rat",
        "date": "2024",
        "duration": 345,
        "is_Explicit": False,
        "original_url_id": "_GHL73Cd4cA",
        "song_id": "_GHL73Cd4cA",
        "song_title": "Nightblood",
        "song_title_clean": "Nightblood",
        "track_count": 9,
        "track_pos": 9,
        "type": "Album",
        "video_type": "MUSIC_VIDEO_TYPE_ATV",
        "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
        "yt_url": "https://www.youtube.com/watch?v=_GHL73Cd4cA"
    }
]



if __name__ == '__main__':
    main()

