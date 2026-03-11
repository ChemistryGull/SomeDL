import json

import argparse
from pathlib import Path

from SomeDL.utils.logging import log, logging
from SomeDL.utils.config import config, generate_config, change_configs, CONFIG_PATH
from SomeDL.utils.version import VERSION, check_latest_version

def parseCliArgs():
      # --- DOC: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="""
Download songs from YouTube by query, multiple queries, or playlist link.

 - Put all inputs in quotes, URLs as well: somedl "Artist - song".
 - Seperate multiple inputs with spaces: somedl "Artist - song" "https://music.youtube..."
 - Different types of URLs and queries can be mixed.
 - Accepted URLs: YT-Music, YT, YT shortened URL, YT playlist. Always include the https://
 - For advanced configuration, use the config file (somedl --generate-config)
 - Downloading a full album by album name is not yet supported""")


    parser.add_argument(
        "inputs",
        nargs="*",  # + One or more inputs | * Zero or more inputs
        help="Song queries (e.g., 'Artist - Song'), YouTube URLs or playlist URLs"
    )

    parser._optionals.title = "General"

    parser.add_argument(
        "--version",
        action="store_true",  # --- Flag, no value needed
        help="Print version"
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help=f'Generate a config file to "{CONFIG_PATH}". Use this config to set format, output folder, output template and more.'
    )

    download_group = parser.add_argument_group("Download")
    download_group.add_argument(
        "-f","--format",
        type=str,
        choices=["best", "best/opus", "best/m4a", "opus", "m4a", "mp3", "vorbis", "flac"],
        metavar="{best, best/opus, best/m4a, opus, m4a, mp3, vorbis, flac}",
        help=f'Select the download format. Default: {config["download"]["format"]}'
    )
    download_group.add_argument(
        "-l","--here",
        action="store_true",
        help="Override the output template and directory and download song in this folder."
    )
    download_group.add_argument(
        "-o","--output",
        type=str,
        metavar="PATH/TO/FOLDER",
        help=f'Select output folder. Default: {config["download"]["output_dir"]}'
    )
    download_group.add_argument(
        "-d", "--download-url-audio",
        action="store_true",
        help="Fetches metadata from youtube search but strictly downloads the audio from the given URL (useful when downloading a specific live video or similar)."
    )


    logging_group = parser.add_argument_group("Logging and debug")
    logging_group.add_argument(
        "-v", "--verbose",
        action="store_true",  # --- Flag, no value needed
        help="Verbose output"
    )
    logging_group.add_argument(
        "-q", "--quiet",
        action="store_true",  # --- Flag, no value needed
        help="Silent all info and warning output. Still prints some info and all errors"
    )
    logging_group.add_argument(
        "-R","--download-report",
        action="store_true",
        help="Use this flag to generate a download report even if there is only one song input."
    )
    logging_group.add_argument(
        "--disable-report",
        action="store_true",
        help="Permanently disable the download report generation. (Revert change in the config file)"
    )
    logging_group.add_argument(
        "--no-download",
        action="store_true",  # --- Flag, no value needed
        help="Only for debug purposes. Skips the yt-dlp download"
    )



    metadata_auth_group = parser.add_argument_group("Metadata & Authentication")
    metadata_auth_group.add_argument(
        "--cookies-from-browser",
        type=str,
        metavar="BROWSER",
        help="To download age restricted music, use this flag and enter the name of your browser where you are logged into youtube with an age-verified account (e.g. firefox). This flag is passed to yt-dlp. More info: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp"
    )
    metadata_auth_group.add_argument(
        "--cookies",
        type=str,
        metavar="FILEPATH",
        help="Path to cookie file. Only required if you want to download age restricted songs from YouTube and the --cookies-from-browser method does not work (common in chromium based browsers like Chrome or Edge). This flag is passed to yt-dlp. More info: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp"
    )
    metadata_auth_group.add_argument(
        "--no-musicbrainz",
        action="store_true",
        help="Use this flag to skip fetching data from MusicBrainz. No genre data will be added!"
    )








    args = parser.parse_args()
    
    if args.verbose:
        config["logging"]["level"] = "DEBUG"

    if args.quiet:
        config["logging"]["level"] = "ERROR"

    match config["logging"]["level"].lower():
        case "debug":
            log.setLevel(logging.DEBUG)
        case "info":
            log.setLevel(logging.INFO)
        case "warning":
            log.setLevel(logging.WARNING)
        case "error":
            log.setLevel(logging.ERROR)
        case "critical":
            log.setLevel(logging.CRITICAL)
        case _:
            log.setLevel(logging.INFO)

    if args.no_download:
        config["download"]["disable_download"] = True
        
    if args.download_url_audio:
        config["download"]["strict_url_download"] = True

    if args.cookies:
        config["download"]["cookies_path"] = args.cookies
    elif args.cookies_from_browser: # --- Only one option is acceptable
        config["download"]["cookies_from_browser"] = args.cookies_from_browser


    if args.no_musicbrainz:
        config["api"]["musicbrainz"] = False

    if args.download_report:
        config["logging"]["download_report"] = 1

    if args.disable_report:
        config["logging"]["download_report"] = 1000000
        change_configs([["logging", "download_report", 1000000]])
        print("Download reports have been disabled.")

    if args.here:
        config["download"]["output"] = "{artist} - {song}"
        config["download"]["output_dir"] = "."

    if args.format:
        config["download"]["format"] = args.format.lower()

    if args.output:
        config["download"]["output_dir"] = args.output



    if args.generate_config:
        generate_config()

    #print(args.format)


    check_latest_version(args.version)


    log.debug(f'Inputs: {args.inputs}')
    # print("Set genre:", args.set_genre)
    # print("Download folder:", args.download_folder)

   

    if len(args.inputs) == 0 and args.version:
        return False
    elif len(args.inputs) == 0:
        log.warning("No inputs provided")
        return False
    else:
        log.debug(f'{len(args.inputs)} inputs provided')
        return args.inputs
