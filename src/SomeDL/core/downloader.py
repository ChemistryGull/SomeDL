import json
import time

import yt_dlp
from yt_dlp.utils import DownloadError
from yt_dlp.utils import render_table

import SomeDL.utils.console as console
from SomeDL.utils.config import config
from SomeDL.utils.utils import sanitize, generateOutputName


def downloadSong(videoID: str, artist: str, album_artist: str, song: str, album, date, track_pos, track_count, label = None):
    # https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#embedding-yt-dlp. 
    #URLS = ['https://music.youtube.com/watch?v=hComisqDS1I']
    URLS = f'https://music.youtube.com/watch?v={videoID}'
    # URLS = f'https://www.youtube.com/watch?v=-X8Olge799M'
    # output_template = sanitize(f'{artist} - {song}')
    output_template = generateOutputName(artist, album_artist, song, album, date, track_pos, track_count)
    console.debug(f'Output path: {str(output_template)}', label)

    console.info("Start yt-dlp download", label)

    ext = config["download"]["format"]
    quality = config["download"]["quality"]


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


    process_handler = YtDlpHandler(label=label)



    ydl_opts = {
        'format': yt_format,
        "outtmpl": output_template + '.%(ext)s',
        "remote_components": ["ejs:github"], # --- https://github.com/yt-dlp/yt-dlp/wiki/EJS
        # 'keepvideo': True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,  # suppress yt-dlps built-in progress bar
        # See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        "logger": process_handler,
        "progress_hooks": [process_handler.progress_hook],
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
            console.debug(f'yt-dlp download successfull. File safed at: {final_filename.get("name")}', label)
        return final_filename.get("name")

    except DownloadError as e:
        console.error(f"yt-dlp download failed.", label)
        console.error(f"Do you have ffmpeg installed? Is the song {URLS} age restricted?", label)
        console.error(f"Perhaps there was a network error, you can try again.", label)
        console.error(f"Error:", label)
        console.error(e, label)
        return False
    except Exception as e:
        console.error(f"Unexpected yt-dlp error: {e}", label)
        return False
    
#downloadSong("A8Mz0Kh7pyw", "Alexandra Căpitănescu", "Choke Me", "Choke Me", 2026, 1, 1)
#downloadSong("ws4aH2iz3j8", "Alexandra Căpitănescu", "Choke Me", "Choke Me", 2026, 1, 1)


class YtDlpHandler:
    def __init__(self, label: str):
        self.label = label

    def debug(self, msg):
        console.debug(f"[bold]>_yt-dlp:[/] {msg}", self.label)

    def warning(self, msg):
        if "No supported JavaScript runtime could be found" in msg:
            console.warning(f"[bold]>_yt-dlp:[/] yt-dlp needs Deno to work properly. It is recommended to install Deno from https://docs.deno.com/runtime/getting_started/installation/.", self.label)
            console.notice(f"[bold]>_yt-dlp:[/] {msg}", self.label)
        elif "Challenge solver lib script version" in msg and "is not supported":
            console.warning(f"[bold]>_yt-dlp:[/] {msg}", self.label)
            console.warning(f"[bold]>_yt-dlp:[/] You may have an outdated yt-dlp-ejs version. Try updating by running [bold]python -m pip install -U \"yt-dlp\\[default]\"[/]", self.label)
        else:
            console.warning(f"[bold]>_yt-dlp:[/] {msg}", self.label)

    def error(self, msg):
        console.error(f"[bold]>_yt-dlp:[/] {msg}", self.label)


    def progress_hook(self, d: dict):

        if d["status"] == "downloading":

            info = {
                "downloaded": d.get("_downloaded_bytes_str"),
                "total": (d.get("_total_bytes_str") or "???").strip(),
                "percent": d.get("_percent_str"),
                "speed": d.get("_speed_str"),
            }

            # text = f'yt-dlp: Downloading [blue]{info["percent"]}[/] - {info["downloaded"]} of {info["total"]} at [green]{info["speed"]}[/]'
            text = f'yt-dlp: Downloading [blue]{info["percent"]}[/] of {info["total"]} at [green]{info["speed"]}[/]'

            console.update(self.label, "downloading", console.Status.ACTIVE, text)
            # time.sleep(0.5)

        elif d["status"] == "finished":

            info = {
                "total": d.get("_total_bytes_str").strip(),
                "percent": d.get("_percent_str"),
                "speed": d.get("_speed_str"),
            }
            
            # text = f'yt-dlp: Postprocessing Downloaded [blue]{info["percent"]}[/] - {info["total"]} at [green]{info["speed"]}[/]'
            # text = f'yt-dlp: Postprocessing  (Finished: [blue]{info["percent"]}[/] - {info["total"]} at [green]{info["speed"]}[/])'
            text = f'yt-dlp: Postprocessing  (Got {info["total"]} at [green]{info["speed"]}[/])'

            console.update(self.label, "downloading", console.Status.ACTIVE, text)
            # time.sleep(2)


