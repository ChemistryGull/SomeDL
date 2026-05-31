"""
This module manages the user configs
"""
import os
import re
import json
import platform
import tomlkit
from pathlib import Path
from importlib.resources import files

import SomeDL.utils.console as console

CONFIG_VERSION = 7

default_config = {
    "metadata": {
        "copyright": (True, bool, None),
        "genre": (True, bool, None),
        "lyrics": (True, bool, None),
        "isrc": (True, bool, None),
        "album_artist": (True, bool, None),
        "multiple_artists": (False, bool, None),
        "artist_separator": ("; ", str, [";", "; ", " ;", " ; ", "/", "/ ", " /", " / "]),
        "ffmpeg_metadata": (False, bool, None),
        "cover_art_file": (False, bool, None),
        "cover_art_size": ("l", str, ["l", "m", "s", "xs", "none"]),
        "lyrics_type": ("plain", str, ["synced", "plain", "both", "synced_if_available", "none"]),
        "synced_lyrics_metadata": (True, bool, None),
        "lrc_file": (False, bool, None),
        "lyrics_id3_synced_uslt_fallback": (False, bool, None),
        "lyrics_source": ("lrclib", str, ["lrclib", "youtube"]),
        "lyrics_fallback_source": ("youtube", str, ["lrclib", "youtube", "none"])
    },
    "download": {
        "format": ("mp3", str, ["best", "best/opus", "best/m4a", "opus", "m4a", "mp3", "vorbis", "flac"]),
        "quality": (5, int, range(0, 10)),
        "id3_version": (3, int, [3, 4]),
        "output_dir": (".", str, None),
        "output": ("{artist} - {song}", str, None),
        #"output": ("{artist}/{album}/{artist} - {song}", str, None),
        # "output": ("{artist}/{year} - {album}/{track_pos} - {song}", str, None),
        "sleep": (0, int, None),
        "sleep_warn": (True, bool, None),
        "disable_download": (False, bool, None),
        "strict_url_download": (False, bool, None), # Default False. True: Only uses search by query for metadata, the audio will be downloaded from the original URL regardless
        "always_search_by_query": (False, bool, None),
        "cookies_path": ("", str, None),
        "cookies_from_browser": ("", str, None), # Maybe add guards there, only certain browsers
        "prefer_playlist": (False, bool, None),
        "fetch_albums": (False, bool, None),
        "number_downloaders": (2, int, range(1, 11)),
        "queue_size": (2, int, range(0, 11)),
        "check_if_file_exists": (True, bool, None),
        "download_archive": ("", str, None),
        "include_singles": (False, bool, None),
        "include_other_artists": (False, bool, None),
        "sync_files": ([], list, None),
        "range": ([], list, None),
    },
    "api": {
        "deezer": (True, bool, None),
        "genius": (True, bool, None),
        "genius_album_check": (True, bool, None),
        "genius_use_official": (False, bool, None),
        "genius_token": ("", str, None),
        "musicbrainz": (True, bool, None),
        "max_retry": (3, int, None),
        "mb_retry_artist_name_only": (False, bool, None), # --- Better keep this false, dont put in user config file
    },
    "logging": {
        "download_report": (2, int, None),
        "level": ("INFO", str, ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        "log_level": (4, int, range(0, 8)),
        "config_version": (4, int, None), # ALWAYS STAY AT 0!!!!!! If this value is ever lost, reset it.
    },
    "webui": {
        "host": ("127.0.0.1", str, None),
        "port": (5000, int, None),
        "open_browser": (True, bool, None),
        "browser": ("", str, None),
    }
}



def get_config_dir(app_name: str) -> Path:
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif system == "Darwin": # Mac-OS
        base = Path.home() / "Library" / "Application Support"
    else:  # Linux and other Unix-like
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    
    config_dir = base / app_name / "somedl_config.toml"
    return config_dir


CONFIG_PATH = (get_config_dir("SomeDL"))
WEBUI_CONFIG_PATH = Path(CONFIG_PATH).with_name("somedl_webui_cache.json")

# === Load data ===

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return tomlkit.parse(f.read())


def load_new_config():
    return files("SomeDL").joinpath("new_somedl_config.toml").read_text()


def load_and_verify_config():
    # console.debug("Loading and verifying config.")
    config = {
        "metadata": {},
        "download": {},
        "api": {},
        "logging": {},
        "webui": {}
    }

    if not check_if_config_exists():
        loaded_config = config
        # console.debug("There is no existing config")
    else:
        loaded_config = load_config()
        # console.debug(f'Config found (Version {loaded_config.get("logging", {}).get("config_version")})')

    
    
    errors = []
    for section, keys in default_config.items():
        # if not section in loaded_config:
        #     raise KeyError(f'Section "{section}" is missing from the config file!')
        for key, (default_value, expected_type, valid_values) in keys.items():
            
            # --- Set to the new value from the config file, if that does not exist, use the default value
            config[section][key] = loaded_config.get(section, {}).get(key, default_value)

            value = config[section][key]
            if not isinstance(value, expected_type) or (expected_type == int and isinstance(value, bool)):
                errors.append(f"{section}.{key}: expected {expected_type.__name__}, got {type(value).__name__}")
            elif valid_values is not None and value not in valid_values:
                errors.append(f"{section}.{key}: '{value}' not in {list(valid_values)}")
    
    if errors:
        console.error("Invalid config:\n" + "\n".join(errors) + "\nPlease check your config\nIf you can't resolve the issue, delete the config file and regenerate it with somedl --generate-config.") # TODO or regenerate it with flag!!
        print()
        raise ValueError("Invalid config file!")

    # printj(config, False)

    # === Special checks ===

    if config["metadata"]["lyrics_source"] == "youtube" and config["metadata"]["lyrics_type"] in ["synced", "both", "synced_if_available"]:
        print("\033[33mWARNING - Youtube does not provide synced lyrics. You have to change the lyrics provider to lrclib if you want synced lyrics.\033[0m")



    return config



# === Change data ===

def change_configs(config_list):
    # --- Change configs to file directly. This should be the only way to edit configs permanently
    # --- config_list = [[section: str, key: str, value: any], ...]

    if not check_if_config_exists():
        generate_config()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        loaded_config = tomlkit.load(f)
        
    for conf in config_list:
        if conf[0] not in loaded_config:
            console.error(f'Config section {conf[0]} is not defined.')
            return
        if conf[1] not in loaded_config.get(conf[0], {}):
            console.error(f'Config {conf[0]}.{conf[1]} is not defined.')
            return
        loaded_config[conf[0]][conf[1]] = conf[2]

    # save_config(loaded_config)


    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        tomlkit.dump(loaded_config, f)



def generate_config(prompt = True):
    new_config = load_new_config()
    # print(new_config)

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if Path(CONFIG_PATH).is_file():
        if prompt:
            answer = input("WARNING - Config file already exists. Do you want to overwrite it? [y/N] > ")
            if not answer.lower() in ["y", "yes"]:
                print("Writing config file canceled.")
                return

    print(f'Generating config in {CONFIG_PATH}')

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(new_config)



def update_config():
    print(f'Updating config to version {CONFIG_VERSION}.')
    new_config = load_new_config()
    new_config_data = tomlkit.parse(new_config)
    old_config = load_and_verify_config()

    for section, keys in new_config_data.items():
        for key, new_value in keys.items():

            # --- Set to the new value from the config file, if that does not exist, use the default value

            new_config_data[section][key] = old_config.get(section, {}).get(key, new_value)


    save_config(new_config_data)
    
def deep_update_config(updates: dict) -> dict:
    # --- Updates all settings in place. Some settings might not apply properly
    for section, values in updates.items():
        if section in config:
            config[section].update(values)


# === Save data ===

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(config))


# === Checks ===

def check_if_config_exists():
    if Path(CONFIG_PATH).is_file():
        return True
    else:
        return False


def check_config_updates(preloaded_config):
    if not preloaded_config["logging"]["config_version"] == CONFIG_VERSION:
        # --- if config is out of date - update it
        # console.debug("Updating config")
        update_config()
        new_config = load_and_verify_config()
        change_configs([["logging", "config_version", CONFIG_VERSION]])
        return new_config
    else:
        # console.debug("Config is up-to-date")
        return preloaded_config
        

# === Load config ===

config = load_and_verify_config()

# if not config["logging"]["config_version"] == 0:
    # --- If version is 0, no confing has been found. keep it that way.
if check_if_config_exists():
    # If file does not exist, there is no reason to do anything.
    config = check_config_updates(config)


# === sync files ===
def generate_new_sync_file(name):
    SYNC_FILE_PATH = Path(CONFIG_PATH).with_name(f"{name}_sync.json")

    if SYNC_FILE_PATH.is_file():
        console.warning("A sync file with this name already exists! Choose another name.")
        console.warning(f'-> {SYNC_FILE_PATH}')
        return

    print(f'Generating new sync file at {SYNC_FILE_PATH}')
    print(f'You can move that file everywhere you want.')
    print(f'To activate the sync file, follow the following steps:')
    print()
    print(f' 1) | Add the full filepath to the \"sync_files\" list in the config file')
    print(f'    | Your config file is located at:')
    print(f'    | {CONFIG_PATH}')
    print()
    print(f' 2) | Add the playlists URLs in the sync file. Each config file can contain as many URLs as you wish.')
    print()
    print(f' 3) | (Optional) Change other settings.')
    print(f'    | All settings defined in the somedl_config.toml can be overwritten with the values set in the sync file.')
    print(f'    | output and output_dir are predefined, you can remove those or add other ones, e.g format etc.')
    print(f'    | The file is in the .json format, adhere to its syntax. SomeDL will return an error if the syntax is not valid.')
    print()
    print(f' 4) | Use the sync file with "somedl sync {name}"')
    print(f'    | ({name}_sync.json becomes {name})')
    print(f'    | Be aware that you can only sync one sync file at a time.')
    
    content = {
        "playlists": ["https://..."],
        "output": config["download"]["output"],
        "output_dir": config["download"]["output_dir"],
    }

    with open(SYNC_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=4)

    
def load_sync_files(sync_files):

    sync_file = sync_files.pop(0)

    if len(sync_files) > 0:
        console.warning(f'You can only sync one sync file at a time. Sync {sync_files} individually. Continuing sync with \"{sync_file}\".')
    else:
        print(f'Syncing {sync_file}')

    # === prepare known sync files ===
    sync_files_list = []
    for entry in config["download"]["sync_files"]:
        item = {"path": Path(entry)}

        item["name"] = item["path"].stem

        if item["name"].endswith("_sync"):
            item["name"] = item["name"][:-5]  # remove "_sync"

        sync_files_list.append(item)

    # === Get data for sync file ===

    path = next((d for d in sync_files_list if d["name"] == sync_file), {}).get("path")

    if not path:
        console.error(f'No sync file "{sync_file}" defined!')
        return

    path = Path(path)

    if not path.is_file():
        console.error(f'No sync file found at: {str(path)}')
        return

    with open(path, "r", encoding="utf-8") as f:
        sync_data = json.load(f)

    playlists = sync_data.pop("playlists")

    # === Override configs with the sync file configs ===
    for config_item in sync_data:

        config_group = ""

        # === check if the item is a config option ===
        if config_item in config["metadata"]:
            config_group = "metadata"
        elif config_item in config["download"]:
            config_group = "download"
        elif config_item in config["api"]:
            config_group = "api"
        elif config_item in config["logging"]:
            config_group = "logging"
        elif config_item in config["webui"]:
            config_group = "webui"
        else:
            console.error(f'Invalid sync file \"{sync_file}\": config item "{config_item}" is not defined')
            return

        default_val, expected_type, valid_values = default_config[config_group][config_item]
        value = sync_data[config_item]

        # == Check for item validity ===
        if not isinstance(value, expected_type) or (expected_type == int and isinstance(value, bool)):
            console.error(f'Invalid sync file \"{sync_file}\": config item "{config_item}": expected {expected_type.__name__}, got {type(value).__name__}')
            return
        elif valid_values is not None and value not in valid_values:
            console.error(f'Invalid sync file \"{sync_file}\": config item "{config_item}": "{value}" not in {list(valid_values)}')
            return

        # === Set the new config value ===
        config[config_group][config_item] = value

    console.debug(f'Playlists: {playlists}')
    return playlists

def list_sync_files():
    print("Available sync files:")

    index = 0
    sync_files_list = []
    print()
    for entry in config["download"]["sync_files"]:
        index += 1
        item = {"path": Path(entry)}

        item["name"] = item["path"].stem

        if item["name"].endswith("_sync"):
            item["name"] = item["name"][:-5]  # remove "_sync"

        print(f'  {str(index).zfill(2)}: {item["name"]} - {item["path"]}')

        sync_files_list.append(item)

    if index == 0:
        print("No sync files defined.")
        print("Generate a new sync file with 'somedl --new-sync-file name'.")
        return []
    
    print()

    while True:
        inp_str = input("Select sync file number > ")
        if inp_str == "":
            inp = 0
            break

        try:
            inp = int(inp_str)
        except ValueError:
            print(f"Invalid input. Enter a number between 1 and {len(sync_files_list)}")
            continue

        if inp > len(sync_files_list):
            print(f"Invalid input. Enter a number between 1 and {len(sync_files_list)}")
            continue

        break

    if not inp:
        return []

    return [sync_files_list[inp - 1]["name"]]


# === WebUI ===
def webui_config_load():
    if not WEBUI_CONFIG_PATH.exists():
        return {}
    
    with open(WEBUI_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def webui_config_save(data):
    WEBUI_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(WEBUI_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
