import re
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from mutagen import File

import SomeDL.utils.console as console
from SomeDL.utils.config import config
from SomeDL.utils.utils import generateOutputName, checkIfFileExists
from SomeDL.core.input_parser import parseSongURL
from SomeDL.core.metadata_helper import metadata_type_cleaner, fetch_metadata, metadata_get_lyrics
from SomeDL.core.metadata import addMetadata, get_audio_metadata, get_audio_metadata_for_update, update_metadata_mutagen
from SomeDL.core.download_report import generateDownloadReport



def import_songs():

    new_log_level = max(config["logging"]["log_level"], 6)
    console.update_log_level(new_log_level)
    config["logging"]["log_level"] = new_log_level

    print()
    print(" ================================== SomeDL - Import ================================== ")
    print()
    print(" Import music files from any folder into your configured folder structure.")
    print(" It will update the metadata in your files in the same way as downloading with SomeDL would.")
    print(" Supported file extentions: mp3, m4a, ogg, opus, flac")
    print()
    print(" This tool is in beta! Always back up your files first, especially when using Move mode.")
    print(" If you want you can share your feedback on this tool (positive or negative) on: https://github.com/ChemistryGull/SomeDL/discussions")
    print()

    print(" 1/6 | Source folder")
    print("     | Folder containing the music files to import.")
    print(f'     | Leave empty to use the current directory: {Path.cwd()}')

    settings = {}

    while True:
        val = input("     |  Path > ") or Path.cwd()
        settings["path_export"] = Path(val)
        if settings["path_export"].exists():
            break
        print("Folder does not exist!")


    print()
    print(" 2/6 | Destination folder")
    print("     | Where imported files will be placed.")
    print("     | Can be a new folder or the folder with your SomeDL downloaded library.")
    print("     | Can not be the same folder as the source folder!")
    print(f'     | Leave empty for default folder: {config["download"]["output_dir"]}')
    print("     | Ignore if you only want to update the metadata of the original files, without moving them.")
 
    while True:
        val = input("     |  Path > ") or Path(config["download"]["output_dir"])
        settings["path_import"] = Path(val)
        if settings["path_import"].exists():
            break
        print("Folder does not exist!")

    config["download"]["output_dir"] = str(settings["path_import"])


    print()
    print(" 3/6 | Output template")
    print("     | Controls how imported files are named and organised.")
    print(f"     | Leave empty to use the configured default: {config['download']['output']}")
    print("     | Ignore if you only want to update the metadata of the original files, without moving them.")
    print("     | Available placeholders: {song} and ({artist} or {album_artist})")
    print("     | Optional Placeholders: {album}, {year}, {track_pos}, {track_count}")
    print("     | Example: {album_artist}/{year} - {album}/{track_pos} - {song}")
    print("     | or       {album_artist}/{album}/{artist} - {song}")
    print("     | or       {album_artist}/{artist} - {song}")
    print("     | or others")
    

    while True:
        out_res = input("     |  New output template > ") or config["download"]["output"]
        if "{song}" in out_res and "artist}" in out_res:
            settings["output"] = out_res
            config["download"]["output"] = settings["output"]
            break
        print("Invalid choice, must at least contain placeholders: {song} and ({artist} or {album_artist})")


    print()

    print(" 4/6 | Import music files recursively?")
    print("     | Should files inside subfolders also be imported?")
    recursive_res = input("     |  [Y/n] > ").lower()

    if recursive_res in ["n", "no"]:
        settings["recursive"] = False
    else:
        settings["recursive"] = True

    print()
    print(" 5/6 | Import mode")
    print("     | Copy - original files are left in place (Recommended unless you have a backup and know what you are doing)")
    print("     | Move - original files are deleted after import")
    print("     | Update - Just update the metadata of the original files. This will neither change the filename nor move the files.")

    while True:
        mode_res = input("     |  [copy/move/update] > ").lower()
        if mode_res in ["c", "copy"]:
            settings["mode"] = "copy"
            break
        if mode_res in ["m", "move"]:
            settings["mode"] = "move"
            break
        if mode_res in ["u", "update"]:
            settings["mode"] = "update"
            config["download"]["output_dir"] = settings["path_export"]
            settings["path_import"] = settings["path_export"]
            config["download"]["check_if_file_exists"] = False
            break
        print("Invalid choice, enter yes or no.")

    print()

    print(" 6/6 | Metadata detection")
    print("     | SomeDL needs to identify each song to update its metadata.")
    print("     | There are several strategies to do so:")
    print("     | A: Video ID in filename, B: artist and title info in filename or C: metadata.")
    print("     | Strategy A can be mixed with B or C as fallback. If B is used C cannot be used.")
    print("     | Please add information to your files:")
    print("     | ")
    print("     | A) Do some of your files contain the YouTube video ID in square brackets?")
    print("     |    This is often the case if your songs were downloaded with yt-dlp")
    print("     |    e.g. The Cold [xI91NneSY5Y].mp3")
    print("     |    Answer Yes if at least some files match.")

    yt_id_res = input("     |     [Y/n] > ").lower()
    if yt_id_res in ["n", "no"]:
        settings["yt_id"] = False
    else:
        settings["yt_id"] = True

    print("     | ")
    print("     | B) Do ALL your filenames follow a \"Artist - Song\" scheme or similar?")
    print("     |    YouTube search will be used to fetch metadata.")
    print("     |    e.g.  Delain - The cold.mp3")
    print("     |    or    Hideaway Paradise by Delain.mp3")
    print("     |    The filename must contain the artist name and the song name.")
    print("     |    !!! Only put Yes if this is the case for every music file in the import folder.")

    # TODO: change to default false
    naming_scheme_res = input("     |     [y/N] > ").lower()
    if naming_scheme_res in ["y", "yes"]:
        settings["naming_scheme"] = True
    else:
        settings["naming_scheme"] = False
    
    if not settings["naming_scheme"]:
        print("     | ")
        print("     | C) Should SomeDL identify songs from metadata already embedded in the files?")
        from_metadata_res = input("     |     [Y/n] > ").lower()
        if from_metadata_res in ["n", "no"]:
            settings["from_metadata"] = False
        else:
            settings["from_metadata"] = True
    else:
        print("     | ")
        print("     | C) Identify by metadata cannot be used as B is set.")

    print()
    print("Settings chosen:")
    print(json.dumps(settings, indent=4, default=str))
    print()

    print("Start import?")
    start = input(" [Y/n] > ")
    if start in ["n", "no"]:
        print("CANCEL IMPORT")
        exit()
    


    # === debug ===
    #settings["path_export"] = Path("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/import_test/exp/")
    # settings["path_import"] = Path("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/import_test/imp/")
    # config["download"]["output_dir"] = Path("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/import_test/imp/")
    # === end debug ===


    # === files loop ===

    folder = Path(settings["path_export"])

    if settings.get("recursive"):
        folder_content = folder.rglob("*")
    else:
        folder_content = folder.glob("*")


    # --- music file extensions
    music_exts = {".mp3", ".flac", ".ogg", ".m4a", ".opus"}
    
    metadata_list = []
    failed_list = []
    already_downloaded_list = []

    # --- Initialize local cache files
    cache_file = settings["path_export"] / "somedl_import_cache"
    if cache_file.exists():
        with cache_file.open("r", encoding="utf-8") as f:
            cache_list = [line.rstrip("\n") for line in f]
    else:
        cache_list = []


    index = 0
    for path in folder_content:
        index += 1
        try:
            file_structure = path.relative_to(settings["path_export"])

            print()
            print(f'--- File Nr. {index} -------------------------------------------------------')
            
            if not path.is_file():
                console.info(f"Folder, not a file: {file_structure}")
                continue

            if str(path) in cache_list:
                console.info(f"File has already been imported: {file_structure}")
                already_downloaded_list.append({"text_query": path})
                continue

            file_extention = path.suffix.lower()
            if file_extention not in music_exts:
                console.info(f"Not a music file: {file_structure}")
                continue

            
            
            console.info(f'Processing {str(file_structure)}')


            metadata = {}

        

            # === Try getting id from yt-dlp id from download ===
            yt_dlp_id_match = re.search(r"(?<=\[)[^\]]{11}(?=\])", str(path))

            if settings.get("yt_id") and yt_dlp_id_match:
                yt_dlp_id = yt_dlp_id_match.group(0)
                console.info(f'Found yt id: {yt_dlp_id}')
                metadata = parseSongURL(yt_dlp_id)


            # === Get data from Artist - Song pairs ===
            if settings.get("naming_scheme") and not metadata:
                console.info(f'Using filename: {path.stem}')
                metadata = {
                    "text_query": path.stem,
                    "video_type": "Search query",
                    "video_type_original": "Search query"
                }

            # === Get data from metadata ===
            if settings.get("from_metadata") and not metadata:
                try: 
                    data = get_audio_metadata(str(path))
                    if data.get("source"):
                        parsed_url = urlparse(data.get("source"))
                        url_queries = parse_qs(parsed_url.query)
                        vid_id = url_queries.get("v", [None])[0]
                        if vid_id:
                            console.info("Using metadata source field")
                            metadata = parseSongURL(vid_id)
                    if not metadata and data.get("artist") and data.get("title"):
                        console.info("Using metadata artist and title fields")
                        metadata = {
                            "text_query": f'{data.get("artist")} - {data.get("title")}',
                            "video_type": "Search query",
                            "video_type_original": "Search query"
                        }
                except Exception as e:
                    console.error(f'Could not get metadata for {path}')
                    print("Error message:")
                    print(e)




            if metadata:

                metadata_type_cleaner(metadata)

                metadata = fetch_metadata(metadata, metadata_list)
                if not metadata:
                    console.warning("Song was not downloaded properly")
                    failed_list.append({"text_query": path})
                    continue
                if metadata == "already_downloaded":
                    already_downloaded_list.append({"text_query": path})
                    with open(cache_file, "a", encoding="utf-8") as f:
                        f.write(f'{path}\n')
                    continue

                if settings.get("mode") == "update":
                    console.debug("Mode is update, do not move file")

                    addMetadata(metadata, path)

                    with open(cache_file, "a", encoding="utf-8") as f:
                        f.write(f'{path}\n')
                    
                    metadata_list.append(metadata)
                    continue


                path_out_raw = generateOutputName(metadata["artist_name"], metadata["album_artist"], metadata["song_title"], metadata["album_name"], metadata["date"], metadata["track_pos"], metadata["track_count"])
                path_out = Path(path_out_raw + file_extention)

                # --- Create path if missing
                path_out.parent.mkdir(parents=True, exist_ok=True)

                # --- Copy/move files over
                if settings.get("mode") == "copy":
                    console.info(f'Copy {path} -> {path_out}')
                    shutil.copy(path, path_out)
                elif settings.get("mode") == "move":
                    console.info(f'Move {path} -> {path_out}')
                    shutil.move(path, path_out)
                else:
                    console.error("Invalid mode")
                    failed_list.append(path)
                    continue

                addMetadata(metadata, path_out)

                with open(cache_file, "a", encoding="utf-8") as f:
                    f.write(f'{path}\n')
                
                metadata_list.append(metadata)
            else:
                failed_list.append({"text_query": path})
                console.error("Could not identify song. Consider enabling different metadata detection strategies (step 6/6)")

        except Exception as e:
            console.critical(f"Critical error while processing file {index}")
    
    print()
    print()
    generateDownloadReport(metadata_list, failed_list, already_downloaded_list)



def update_storage_template():

    new_log_level = max(config["logging"]["log_level"], 6)
    console.update_log_level(new_log_level)
    config["logging"]["log_level"] = new_log_level

    print()
    print(" ============================= SomeDL - New output template ============================= ")
    print()
    print(" Utility to automatically move/copy your current library to a new storage template.")
    print(" You can also sort songs downloaded with SomeDL from another folder into your music library.")
    print(" This tool assumes it is used on files with complete metadata, it does not change metadata.")
    print(" If you want to organize a library with incomplete metadata, use 'somedl import' instead.")
    print()
    print(" This tool is in beta! Always back up your files first, especially when using Move mode.")
    print(" If you want you can share your feedback on this tool (positive or negative) on: https://github.com/ChemistryGull/SomeDL/discussions")
    print()
    # print(" This tool moves/copies your files into a new folder with your prefered storage template.")
    # print(" You can temporary rename your music library with the old folder template.")
    print()

    print(" 1/4 | Source folder")
    print("     | Your old music library folder, or the folder containing the files you want to sort into your library")

    settings = {}

    while True:
        settings["path_export"] = Path(input("     |  Path > "))
        if settings["path_export"].exists():
            break
        print("Folder does not exist!")


    print()
    print(" 2/4 | Destination folder")
    print("     | Your new music library folder")
 
    while True:
        settings["path_import"] = Path(input("     |  Path > "))
        if settings["path_import"].exists():
            break
        print("Folder does not exist!")

    config["download"]["output_dir"] = str(settings["path_import"])


    print()
    print(" 3/4 | NEW output template")
    print("     | Available placeholders: {song} and ({artist} or {album_artist})")
    print("     | Optional Placeholders: {album}, {year}, {track_pos}, {track_count}")
    print("     | Example: {album_artist}/{year} - {album}/{track_pos} - {song}")
    print("     | or       {album_artist}/{album}/{artist} - {song}")
    print("     | or       {album_artist}/{artist} - {song}")
    print("     | or others")

    while True:
        out_res = input("     |  New output template > ")
        if "{song}" in out_res and "artist}" in out_res:
            settings["output"] = out_res
            config["download"]["output"] = settings["output"]
            break
        print("Invalid choice, must at least contain placeholders: {song} and ({artist} or {album_artist})")



    print()
    print(" 4/4 | Mode")
    print("     | Copy - original files are left in place (Recommended unless you have a backup and know what you are doing)")
    print("     | Move - original files are deleted after import")

    while True:
        mode_res = input("     |  [copy/move] > ").lower()
        if mode_res in ["c", "copy"]:
            settings["mode"] = "copy"
            break
        if mode_res in ["m", "move"]:
            settings["mode"] = "move"
            break
        print("Invalid choice, enter copy or move.")


    print()
    print("Settings chosen:")
    print(json.dumps(settings, indent=4, default=str))
    print()

    print("Start process?")
    start = input(" [Y/n] > ")
    if start in ["n", "no"]:
        print("CANCEL")
        exit()
    


    # === debug ===
    # settings["path_export"] = Path("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/import_test/imp/")
    # settings["path_import"] = Path("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/import_test/new/")
    # config["download"]["output_dir"] = Path("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/import_test/new/")
    # === end debug ===


    # === files loop ===


    folder = Path(settings["path_export"])

    

    # --- music file extensions
    music_exts = {".mp3", ".flac", ".ogg", ".m4a", ".opus"}
    
    metadata_list = []
    failed_list = []
    already_downloaded_list = []

    # --- Initialize local cache files
    cache_file = settings["path_export"] / "somedl_new_template_cache"
    if cache_file.exists():
        with cache_file.open("r", encoding="utf-8") as f:
            cache_list = [line.rstrip("\n") for line in f]
    else:
        cache_list = []


    index = 0
    for path in folder.rglob("*"):
        index += 1
        try:
            file_structure = path.relative_to(settings["path_export"])

            print()
            print(f'--- File Nr. {index} -------------------------------------------------------')
            
            if not path.is_file():
                console.info(f"Folder, not a file: {file_structure}")
                with open(cache_file, "a", encoding="utf-8") as f:
                    f.write(f'{path}\n')
                continue

            if str(path) in cache_list:
                console.info(f"File has already been imported (cache file): {file_structure}")
                already_downloaded_list.append({"text_query": path})
                continue

            file_extention = path.suffix.lower()
            if file_extention not in music_exts:
                console.info(f"Not a music file: {file_structure}")
                with open(cache_file, "a", encoding="utf-8") as f:
                    f.write(f'{path}\n')
                continue

            
            
            console.info(f'Processing {str(file_structure)}')



            try: 
                data = get_audio_metadata(str(path))
                
            except Exception as e:
                console.error(f'Could not get metadata for {path}')
                print("Error message:")
                print(e)
                failed_list.append({"text_query": path})
                continue

            if checkIfFileExists(data["artist"], data["title"], data["album_artist"]):
                console.info(f"File has already been imported: {file_structure}")
                already_downloaded_list.append({"text_query": path})
                continue


            if data:
                console.info("Got data for song")


                path_out_raw = generateOutputName(data["artist"], data["album_artist"], data["title"], data["album"], data["year"], data["track_pos"], data["track_count"])
                path_out = Path(path_out_raw + file_extention)

                # --- Create path if missing
                path_out.parent.mkdir(parents=True, exist_ok=True)

                # --- Copy/move files over
                if settings.get("mode") == "copy":
                    console.info(f'Copy {path} -> {path_out}')
                    shutil.copy(path, path_out)
                elif settings.get("mode") == "move":
                    console.info(f'Move {path} -> {path_out}')
                    shutil.move(path, path_out)
                else:
                    console.error("Invalid mode")
                    failed_list.append(path)
                    continue

                if path.with_suffix(".lrc").is_file():
                    if settings.get("mode") == "copy":
                        console.info(f'Copy {path.with_suffix(".lrc")} -> {path_out.with_suffix(".lrc")}')
                        shutil.copy(path.with_suffix(".lrc"), path_out.with_suffix(".lrc"))
                    elif settings.get("mode") == "move":
                        console.info(f'Move {path.with_suffix(".lrc")} -> {path_out.with_suffix(".lrc")}')
                        shutil.move(path.with_suffix(".lrc"), path_out.with_suffix(".lrc"))
                    else:
                        console.error("Invalid mode")
                        failed_list.append(path)
                        continue

                
                metadata_list.append({
                    "artist_name": data.get("artist"),
                    "song_title": data.get("title"),
                    "album_name": data.get("album"),
                    "album_artist": data.get("album_artist"),
                    "date": data.get("year"),
                    "track_pos": data.get("track_pos"),
                    "track_count": data.get("track_count"),
                    "yt_url": data.get("source"),
                })

                with open(cache_file, "a", encoding="utf-8") as f:
                    f.write(f'{path}\n')

            else:
                failed_list.append({"text_query": path})
                console.error("Failed to add file")

        except Exception as e:
            console.critical(f"Critical error while processing file {index}")

    print()
    print("Ignore the genre, lyrics etc field in the download report. Metadata has not been changed.")
    generateDownloadReport(metadata_list, failed_list, already_downloaded_list)




# Unused addition, may work on in the future
def update_metadata():
    new_log_level = max(config["logging"]["log_level"], 6)
    console.update_log_level(new_log_level)
    config["logging"]["log_level"] = new_log_level

    settings = {
        "folder": "",
        "mode": "add",
        "genre": False,
        "synced_lyrics": True,
        "plain_lyrics": False,
    }

    print()
    print(" ============================= SomeDL - Update Metadata ============================= ")
    print()
    print(" Utility to update or redownload missing metadata. Currently only supports updating lyrics")
    print()
    print(" ATTENTION: I've done little testing with this utility, please test it on a small amount of disposable files first!!")
    print(" ATTENTION: The settings in your config file must reflect the update that you want to make")
    print("            e.g. if you want to add or update synced lyrics, but have disabled synced lyrics in the config, this won't work.")
    print(" If you want you can share your feedback on this tool (positive or negative) on: https://github.com/ChemistryGull/SomeDL/discussions")
    print()
    # print(" This tool moves/copies your files into a new folder with your prefered storage template.")
    # print(" You can temporary rename your music library with the old folder template.")
    print()

    print(" 1/3 | Source folder")
    print("     | Your old music library folder, or the folder containing the files you want to sort into your library")

    settings = {}

    while True:
        settings["folder"] = Path(input("     |  Path > "))
        if settings["folder"].exists():
            break
        print("Folder does not exist!")

    print()

    print(" 2/3 | Mode")
    print("     | Add - Only add missing data")
    print("     | Update - Update all data, even if already present")

    while True:
        mode_res = input("     |  [add/update] > ").lower()
        if mode_res in ["a", "add"]:
            settings["mode"] = "add"
            break
        if mode_res in ["u", "update"]:
            settings["mode"] = "update"
            break
        print("Invalid choice, enter add or update.")

    print()
    
    print(" 3/3 | What to update")
    print("     | ")
    print("     | 1) Plain Lyrics")

    while True:
        mode_res = input("     |  [y/n] > ").lower()
        if mode_res in ["y", "yes"]:
            settings["plain_lyrics"] = True
            break
        if mode_res in ["n", "no"]:
            settings["plain_lyrics"] = False
            break
        print("Invalid choice, enter yes or no.")

    print("     | ")
    print("     | 2) Synced Lyrics")

    while True:
        mode_res = input("     |  [y/n] > ").lower()
        if mode_res in ["y", "yes"]:
            settings["synced_lyrics"] = True
            break
        if mode_res in ["n", "no"]:
            settings["synced_lyrics"] = False
            break
        print("Invalid choice, enter yes or no.")


    print()
    print("Settings chosen:")
    print(json.dumps(settings, indent=4, default=str))
    print()

    print("Start process?")
    start = input(" [Y/n] > ")
    if start in ["n", "no"]:
        print("CANCEL")
        exit()


    folder = Path(settings["folder"])


    # --- music file extensions
    music_exts = {".mp3", ".flac", ".ogg", ".m4a", ".opus"}
    

    

    # === Precheck if config is right ===

    if (settings["synced_lyrics"] or settings["plain_lyrics"]) and not config["metadata"]["lyrics"]:
        console.warning('You need to enable "lyrics" in the configs to update lyrics')
        return

    if settings["synced_lyrics"] and not config["metadata"]["lyrics_type"] in ["synced", "both", "synced_if_available"]:
        console.warning('You need to set "lyrics_type" to "synced", "both" or "synced_if_available" in the config file if you want to update synchronized lyrics')
        return
    
    if settings["plain_lyrics"] and not config["metadata"]["lyrics_type"] in ["plain", "both"]:
        console.warning('You need to set "lyrics_type" to ""plain" or "both" in the config file if you want to update plain lyrics')
        return


    cache_file = folder / "somedl_new_template_cache"
    if cache_file.exists():
        with cache_file.open("r", encoding="utf-8") as f:
            cache_list = [line.rstrip("\n") for line in f]
    else:
        cache_list = []




    index = 0
    for path in folder.rglob("*"):
        index += 1
        try:

            print()
            print(f'--- File Nr. {index} -------------------------------------------------------')
            print(f'-> {path.name}')


            if not path.is_file():
                console.info(f"Folder, not a file: {path}")
                with open(cache_file, "a", encoding="utf-8") as f:
                    f.write(f'{path}\n')
                continue

            if str(path) in cache_list:
                console.info(f"File has already been imported (cache file)")
                continue

            file_extention = path.suffix.lower()
            if file_extention not in music_exts:
                console.info(f"Not a music file: {path}")
                with open(cache_file, "a", encoding="utf-8") as f:
                    f.write(f'{path}\n')
                continue



            data = get_audio_metadata_for_update(str(path))
            
            if data.get("source"):
                parsed_url = urlparse(data.get("source"))
                url_queries = parse_qs(parsed_url.query)
                vid_id = url_queries.get("v", [None])[0]
            else:
                console.error("File does not contain source tag. It was likely not downloaded using SomeDL, use 'somedl import' instead.")
                continue



            fetched_lyrics_already = False

            data_to_update = {
                "synced_lyrics": None,
                "plain_lyrics": None,
                "genre": None,
                "mb_artist_id": None
            }

            if settings["synced_lyrics"]:

                if settings["mode"] == "update" or (settings["mode"] == "add" and not data.get("lyrics_synced")):
                    console.info("Looking for synced lyrics")
                    result = metadata_get_lyrics(artist_name = data.get("artist"), song_title= data.get("title"), duration = data.get("duration"), song_id = vid_id)
                    fetched_lyrics_already = True

                    data_to_update["synced_lyrics"] = result.get("lyrics_synced")

                else:
                    console.info("[cyan]Synced lyrics already present[/]")

            if settings["plain_lyrics"]:
                if settings["mode"] == "update" or (settings["mode"] == "add" and not data.get("lyrics_unsynced")):
                    console.info("Looking for plain lyrics")

                    if not fetched_lyrics_already:
                        result = metadata_get_lyrics(artist_name = data.get("artist"), song_title= data.get("title"), duration = data.get("duration"), song_id = vid_id)


                    data_to_update["plain_lyrics"] = result.get("lyrics_plain")
                else:
                    console.info("[cyan]Plain lyrics already present[/]")
            # if settings["genre"]:
            #     if settings["mode"] == "update" or (settings["mode"] == "add" and not data.get("genre")):
            #         console.info("Looking for genre on musicbrainz")

            something_to_update = False

            if data_to_update["synced_lyrics"]:
                console.info("[green]Updating synced lyrics[/]")
                something_to_update = True
                # print(data_to_update["synced_lyrics"])
            
            if data_to_update["plain_lyrics"]:
                console.info("[green]Updating plain lyrics[/]")
                something_to_update = True
                # print(data_to_update["plain_lyrics"])

            if something_to_update:
                update_metadata_mutagen(path, synced_lyrics = data_to_update["synced_lyrics"], plain_lyrics = data_to_update["plain_lyrics"])
            else:
                console.info("[yellow]Nothing to update or no data found[/]")


            with open(cache_file, "a", encoding="utf-8") as f:
                f.write(f'{path}\n')
        except Exception as e:
            console.error("Critical error while processing this file: ")
            console.error(e)

    print()
    print("Finished. somedl update-metadata does not yet support download report")
    #generateDownloadReport(metadata_list, failed_list, already_downloaded_list)


# printj(get_audio_metadata("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.flac"))
# printj(get_audio_metadata("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.m4a"))
# printj(get_audio_metadata("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.mp3"))
# printj(get_audio_metadata("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.ogg"))
# printj(get_audio_metadata("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.opus"))


