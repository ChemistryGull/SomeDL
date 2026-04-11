import time
import queue

from SomeDL.utils.config import config
import SomeDL.utils.console as console
from SomeDL.utils.version import VERSION
from SomeDL.core.input_parser import generateSongList
from SomeDL.core.metadata_helper import fetch_albums
from SomeDL.core.cli_parser import parseCliArgs
from SomeDL.core.download_report import generateDownloadReport
from SomeDL.core.processor import process_song_list_concurrent
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

    # === Convert songs_list to queue ===
    song_list_queue: queue.Queue = queue.Queue()
    for item in songs_list:
        song_list_queue.put(item)

    # === Main Process loop ===
    console.print_header(config["logging"]["log_level"], VERSION)

    metadata_success_list, failed_list, already_downloaded_list = process_song_list_concurrent(song_list_queue, oneshot = True)
    # metadata_success_list, failed_list, already_downloaded_list = process_song_list_concurrent(songs_list)

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

