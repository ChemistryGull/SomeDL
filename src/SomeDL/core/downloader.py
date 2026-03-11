import json

import yt_dlp
from yt_dlp.utils import DownloadError
from yt_dlp.utils import render_table

from SomeDL.utils.logging import log, printj
from SomeDL.utils.config import config
from SomeDL.utils.utils import sanitize
from SomeDL.utils.utils import generateOutputName


def downloadSong(videoID: str, artist: str, song: str, album, date, track_pos, track_count): 
    # https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#embedding-yt-dlp. 
    #URLS = ['https://music.youtube.com/watch?v=hComisqDS1I']
    URLS = f'https://music.youtube.com/watch?v={videoID}'
    #URLS = f'https://www.youtube.com/watch?v=-X8Olge799M'
    # output_template = sanitize(f'{artist} - {song}')
    output_template = generateOutputName(artist, song, album, date, track_pos, track_count)

    log.info("Start yt-dlp download...")

    ext = config["download"]["format"]
    quality = config["download"]["quality"]
    if config["logging"]["level"].lower() == "debug":
        yt_quiet = False
    else:
        yt_quiet = True

    # # --- Options: ["best", "best/opus", "best/m4a", "opus", "m4a", "mp3", "vorbis", "flac"]
    # flac is not recommended! You are limited to the quality youtube provides, reencoding to flac just results in huge file sizes with no benefit
    
    postprocessors = []
    yt_format = "bestaudio/best"
    final_filename = {}

    if ext == "best":
        yt_format = "bestaudio/best"
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'best',
        }]
    elif ext == "best/opus":
        yt_format = "bestaudio[ext=opus]/bestaudio/best"
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'best',
        }]
    elif ext == "best/m4a":
        yt_format = "bestaudio[ext=m4a]/bestaudio/best"
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'best',
        }]
    elif ext == "m4a":
        yt_format = "bestaudio[ext=m4a]/bestaudio/best"
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    elif ext == "opus":
        yt_format = "bestaudio[ext=opus]/bestaudio/best"
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
        }]
    elif ext == "mp3":
        yt_format = "bestaudio[ext=m4a]/bestaudio/best"
        postprocessors = [{ 
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }]
    elif ext == "vorbis":
        yt_format = "bestaudio/best"
        postprocessors = [{ 
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'vorbis',
            'preferredquality': quality,
        }]
    elif ext == "flac":
        yt_format = "bestaudio/best"
        postprocessors = [{ 
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'flac',
            'preferredquality': quality,
        }]


    ydl_opts = {
        'format': yt_format,
        #'format': 'bestaudio*',
        #'format': 'bestaudio[ext=m4a]/bestaudio/best',
        "remote_components": ["ejs:github"], # --- https://github.com/yt-dlp/yt-dlp/wiki/EJS
        "outtmpl": output_template + '.%(ext)s',
        # 'keepvideo': True,
        "quiet": yt_quiet,
        # "no_warnings": True,
        # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': postprocessors,
        'post_hooks': [lambda f: final_filename.update({'name': f})] # --- Contains the filename of the output file
    }

    if config["download"]["cookies_from_browser"]:
        ydl_opts["cookiesfrombrowser"] = (config["download"]["cookies_from_browser"],) # --- Needs to be a tuple

    if config["download"]["cookies_path"]:
        ydl_opts["cookiefile"] = config["download"]["cookies_path"]
    try: 
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # info = ydl.extract_info(URLS, download=False)  # get metadata only
            # ydl.list_formats(info)  # equivalent to `yt-dlp -F`
            error_code = ydl.download(URLS)
            log.debug(f'yt-dlp download successfull. File safed at: {final_filename.get("name")}')
        return final_filename.get("name")

    except DownloadError as e:
        log.error(f"yt-dlp download failed. Do you have ffmpeg installed? Is the song {URLS} age restricted?: {e}")
        return False
    except Exception as e:
        log.error(f"Unexpected yt-dlp error: {e}")
        return False
    
#downloadSong("A8Mz0Kh7pyw", "Alexandra Căpitănescu", "Choke Me", "Choke Me", 2026, 1, 1)
#downloadSong("ws4aH2iz3j8", "Alexandra Căpitănescu", "Choke Me", "Choke Me", 2026, 1, 1)
