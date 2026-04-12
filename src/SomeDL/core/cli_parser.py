import json

import argparse
from pathlib import Path

import SomeDL.utils.console as console
from SomeDL.utils.config import config, generate_config, change_configs, CONFIG_PATH, check_if_config_exists
from SomeDL.utils.version import VERSION, check_latest_version
from SomeDL.utils.utils import read_archive_file

def parseCliArgs():
    # --- DOC: https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="""
Download songs from YouTube by query, multiple queries, or playlist link.

 - Put all inputs in quotes, URLs as well:  somedl "Artist - song"
 - Seperate multiple inputs with spaces:    somedl "Artist - song" "https://music.youtube..." "https://youtube.com/..."
 - Different types of URLs and queries can be mixed.
 - For advanced configuration, use the config file (somedl --generate-config)
 - Special utilities (in beta):
 - somedl import        Import songs downloaded with other tools, or update the metadata of your existing library.
 - somedl new-template  Move or copy your existing library to a new output template""")


    # === Main Parser ===
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
    parser.add_argument(
        "--show-config",
        action="store_true",
        help=f'Show the current configurations.'
    )


    # === Download ===

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
    download_group.add_argument(
        "--get-song",
        action="store_true",
        help=f'When the url contains both playlist and song ID, only download the current song. {"" if config["download"]["prefer_playlist"] else "(Default)"}'
    )
    download_group.add_argument(
        "--get-playlist",
        action="store_true",
        help=f'When the url contains both playlist and song ID, download the entire playlist. {"" if not config["download"]["prefer_playlist"] else "(Default)"}'
    )
    download_group.add_argument(
        "--fetch-albums",
        action="store_true",
        help="Download the entire albums from all requested songs, even from within playlists."
    )
    download_group.add_argument(
        "--no-album",
        action="store_true",
        help="Override fetch-albums setting and fetch only a single track."
    )
    download_group.add_argument(
        "--download-archive",
        type=str,
        metavar="PATH/TO/FOLDER",
        help="Add song IDs to a archive file. Only download videos that have not been added to the archive already."
    )
    download_group.add_argument(
        "--skip-file-check",
        action="store_true",
        help="Download songs even if they are already present in the output folder."
    )
    download_group.add_argument(
        "--redownload",
        action="store_true",
        help="Download songs even if they are already present or in a download archive."
    )
    download_group.add_argument(
        "--include-singles",
        action="store_true",
        help="Applies only to artist/channel URLs: Also download Singles and EPs (often duplicates)"
    )
    download_group.add_argument(
        "--include-other-artists",
        action="store_true",
        help="Applies only to artist/channel URLs: also download albums with a different album artist."
    )


    # === Logging ===

    logging_group = parser.add_argument_group("Logging and debug")
    logging_group.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Verbose output, -vv and -vvv for even more verbose output"
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


    # === Metadata and authentication ===

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
        help="Skip fetching data from MusicBrainz. No genre data will be added!"
    )
    metadata_auth_group.add_argument(
        "--no-album-check",
        action="store_true",
        help="Always use the metadata provided by YouTube without cross-checking it against Genius. This will cause some songs to be downloaded as singles instead of as part of an album."
    )






    # === Parsing of the arguments ===

    args = parser.parse_args()
    
    config["logging"]["log_level"] = 4 + args.verbose # --- Default 4, increase with every -v flag
    console.update_log_level(4 + args.verbose)

    if args.quiet:
        config["logging"]["log_level"] = 2
        console.update_log_level(2)


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
    if args.no_album_check:
        config["api"]["genius_album_check"] = False


    if args.download_report:
        config["logging"]["download_report"] = 0

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

    if args.show_config:
        if check_if_config_exists():
            print(f'Config saved at: "{CONFIG_PATH}"')
            print("Current config:")
            console.printj(config)
            print()
        else:
            print("No configuragtion file set.")
            print("To generate a config file, run \"somedl --generate-config\"")
            print("The config file will then be available at:")
            print(CONFIG_PATH)
            print()
            print("Default confiurations apply:")
            console.printj(config)
            print()
        return False


    if args.get_playlist:
        config["download"]["prefer_playlist"] = True
    if args.get_song:
        config["download"]["prefer_playlist"] = False

    if args.fetch_albums:
        config["download"]["fetch_albums"] = True
    if args.no_album:
        config["download"]["fetch_albums"] = False


    if args.download_archive:
        config["download"]["download_archive"] = args.download_archive
    
    read_archive_file()

    if args.skip_file_check:
        config["download"]["check_if_file_exists"] = False

    if args.redownload:
        config["download"]["check_if_file_exists"] = False
        config["download"]["download_archive"] = ""

    if args.include_singles:
        config["download"]["include_singles"] = True
    if args.include_other_artists:
        config["download"]["include_other_artists"] = True


    #print(args.format)


    check_latest_version(args.version)


    console.debug(f'Inputs: {args.inputs}')
    # print("Set genre:", args.set_genre)
    # print("Download folder:", args.download_folder)

   

    if len(args.inputs) == 0 and args.version:
        return False
    elif len(args.inputs) == 0:
        console.warning("No inputs provided")
        return False
    else:
        console.debug(f'{len(args.inputs)} inputs provided')
        return args.inputs
