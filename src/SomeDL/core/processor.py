import json
import time
import re
import random
import traceback

import threading
import queue

from rich.live import Live


from SomeDL.utils.config import config
import SomeDL.utils.console as console
from SomeDL.utils.console import thread_lock
from SomeDL.core.metadata_helper import fetch_metadata, metadata_type_cleaner
from SomeDL.core.downloader import downloadSong
from SomeDL.core.metadata import addMetadata


# === Main loop that loops through all songs ===

def process_song_list_concurrent(song_list_queue: queue.Queue, oneshot: bool = True, metadata_success_list: list = [], failed_list: list = [], already_downloaded_list: list = []):

    # === Shared variables ===

    _DONE = object()
    NUM_DOWNLOADERS = config["download"]["number_downloaders"]
    QUEUE_MAXSIZE = config["download"]["queue_size"]

    download_queue: queue.Queue = queue.Queue(maxsize=QUEUE_MAXSIZE)

    # metadata_success_list: list = []
    # failed_list: list = []
    # already_downloaded_list: list = []

    if oneshot:
        song_list_queue.put(_DONE)

    # === Metadata fetching thread ===
    def thread_fetch_metadata(song_list_queue):
        metadata_list = []
        
        index = 0
        length = song_list_queue.qsize()
        if oneshot:
            length -= 1

        while True:
            console.pause_event.wait() # --- To pause from the web ui

            item = song_list_queue.get()


            if item is _DONE:
                break
            
            index += 1

            if item.get("text_query"):
                label = {
                    "text": f'{index}/{length} {item.get("text_query")}',
                    "id": item.get("somedl_id")
                }
            else:
                label = {
                    "text": f'{index}/{length} {item.get("artist_name")} - {item.get("song_title")}',
                    "id": item.get("somedl_id")
                }
            item["label"] = label

            console.init(label)

            console.pause_event.wait() # --- Catch pause if pause is made on an empty queue. Has to be after initiating the item as active
            
            try:
                # === clean metadata ===
                clean_success = metadata_type_cleaner(item)

                if not clean_success:
                    console.warning(f'Song could not be downloaded, error on initial lookup.', item["label"])
                    console.finish(item.get("label"), console.Download_status.FAILED)
                    with console.thread_lock:
                        item["error"] = "Song could not be downloaded, error on initial lookup. That video may not be a song. Try looking the song up on YouTube Music or via the SomeDL WebUI (somedl web)."
                        failed_list.append(item)
                    continue

                # === Create the real label after cleaning metadata. ===
                label = {
                    "text": f'{index}/{length} {item.get("artist_name")} - {item.get("song_title")}',
                    "id": item.get("somedl_id")
                }
                item["label"] = label

                # === Check if the song was already in the queue ===
                # --- (Necessary for when the same song is currently being downloaded already, but not yet in the download folder. Avoids yt-dlp accessign same file errors)
                # --- NEVER ADD ANYTHING WITH console.update BEFORE THIS LINE!!!!!!!!
                item_already_being_processed = False
                with console.thread_lock:
                    if any(not item["data"] == {} and item.get("text").split(" ", 1)[1] == label["text"].split(" ", 1)[1] for ID, item in console.active_items.items()):
                        item_already_being_processed = True 

                if item_already_being_processed:
                    # --- This has to be outside the above with console.thread_lock, as else it would cause a deadlock (thread_lock called in a thread_lock).
                    console.info("This input is a duplicate", item["label"])
                    console.finish(item.get("label"), console.Download_status.ALREADY_DOWNLOADED)
                    item["path"] = None
                    already_downloaded_list.append(item)
                    continue


                # === fetch metadata ===
                
                metadata = fetch_metadata(item, metadata_list)

                if not metadata:
                    console.warning("Song could not be downloaded, error on metadata fetching.", item["label"])
                    console.finish(item.get("label"), console.Download_status.FAILED)
                    with console.thread_lock:
                        item["error"] = "Song could not be downloaded, error on metadata fetching."
                        failed_list.append(item)
                    continue

                if metadata.get("already_downloaded"):
                    console.finish(item.get("label"), console.Download_status.ALREADY_DOWNLOADED, path=metadata.get("path"))
                    item["path"] = metadata.get("path")

                    with console.thread_lock:
                        already_downloaded_list.append(item)
                    continue

                metadata_list.append(metadata) # --- Used for known_metadata

                if config["download"]["disable_download"]:
                    # time.sleep(100)
                    console.update(label, "disable_download", console.Status.SKIPPED)
                    console.notice("Not downloading song because disable-download is set", item["label"])
                    console.finish(label, console.Download_status.DOWNLOAD_DISABLED)

                    with console.thread_lock:
                        metadata_success_list.append(metadata)
                    continue

                console.update(label, "wait_queue", console.Status.ACTIVE, "Queuing for download")

                download_queue.put(metadata) # ---- blocks when queue is full

                console.update(label, "wait_queue", console.Status.ACTIVE, "Queuing for download (in queue)")
            
            except FileNotFoundError as e:
                console.error("Critical error:")
                console.error(e)

            except Exception as e:
                console.error("A critical exception occured when fetching the metadata for this song! If retrying does not help, please notify the program maintainer at https://github.com/ChemistryGull/SomeDL. Error:", label)
                console.error(e, label)
                traceback.print_exc()
                console.finish(label, console.Download_status.FAILED)
                with console.thread_lock:
                    item["error"] = str(e)
                    failed_list.append(item)


        for _ in range(NUM_DOWNLOADERS):
            download_queue.put(_DONE)


    # === Downloader thread ===
    def thread_downloader(thread_id: int) -> None:
        while True:
            console.pause_event.wait() # --- To pause from the web ui

            metadata = download_queue.get()
            if metadata is _DONE:
                break
            
            label = None
            try:
                timer_start = time.time()
                label = metadata.get("label")

                sleep_time = config["download"]["sleep"] + random.uniform(0, 5)

                if config["download"]["sleep"]:
                    console.update(label, "wait_queue", console.Status.ACTIVE, f'yt-dlp: Sleeping for {round(sleep_time, 1)} seconds.')
                    time.sleep(sleep_time) # --- Adds random amount of seconds 0-5 to the sleep timer
                
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
                    metadata["path"] = filename
                    metadata["filetype"] = filename.rsplit(".", 1)[-1]
                    with console.thread_lock:
                        metadata_success_list.append(metadata)

                    console.finish(label, console.Download_status.SUCCESS, path=filename)
                else: 
                    console.error("File could not be downloaded using yt-dlp", label)
                    console.update(label, "downloading", console.Status.FAILED)
                    console.finish(label, console.Download_status.FAILED)
                    with console.thread_lock:
                        metadata["error"] = "File could not be downloaded using yt-dlp. Retrying might help."
                        failed_list.append(metadata)
                    continue

                # === Timer ===
                timer_end = time.time()
                length = timer_end - timer_start
                console.info(f'TIME - Download time: {length} seconds.', metadata.get("label"))
                metadata["download_time"] = length
                metadata["total_time"] = f'{round(metadata["download_time"] + metadata.get("metadata_time", 0), 1)} seconds' 
                
                # === Add line to download archive if enabled ===
                if config["download"]["download_archive"]:
                    with open(config["download"]["download_archive"], "a", encoding="utf-8") as f:
                        f.write(f'{metadata["song_id"]}\n')

            except Exception as e:
                console.error("A critical exception occurred when trying to download song with yt-dlp! If retrying does not help, please notify the program maintainer at https://github.com/ChemistryGull/SomeDL. Error:", label)
                console.error(e, label)
                traceback.print_exc()
                console.finish(label, console.Download_status.FAILED)
                with console.thread_lock:
                    metadata["error"] = str(e)
                    failed_list.append(metadata)

            download_queue.task_done()



    with Live(console.make_table(), refresh_per_second=10, transient=True) as live:
        console.init_live(live)

        threads = (
            [threading.Thread(target=thread_fetch_metadata, args=(song_list_queue,), daemon=True)]
            # [threading.Thread(target=thread_fetch_metadata, args=(songs_list,), daemon=True)]
            + [threading.Thread(target=thread_downloader, args=(i + 1,), daemon=True) for i in range(NUM_DOWNLOADERS)]
        )
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        console.clear_live(live)

    
    return metadata_success_list, failed_list, already_downloaded_list

