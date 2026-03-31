"""
This module manages the user configs
"""
import os
import platform
import tomlkit
from pathlib import Path
from importlib.resources import files

import SomeDL.utils.console as console

CONFIG_VERSION = 4

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
        "disable_download": (False, bool, None),
        "strict_url_download": (False, bool, None), # Default False. True: Only uses search by query for metadata, the audio will be downloaded from the original URL regardless
        "always_search_by_query": (False, bool, None),
        "cookies_path": ("", str, None),
        "cookies_from_browser": ("", str, None), # Maybe add guards there, only certain browsers
        "prefer_playlist": (False, bool, None),
        "fetch_albums": (False, bool, None), # todo
        "check_if_file_exists": (True, bool, None),
        "number_downloaders": (2, int, range(1, 11)),
        "queue_size": (2, int, range(0, 11)),
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
        "config_version": (4, int, None), # If this value is ever lost, reset it
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
        "logging": {}
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



def generate_config():
    new_config = load_new_config()
    # print(new_config)

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if Path(CONFIG_PATH).is_file():
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

if not config["logging"]["config_version"] == 0:
    # --- If version is 0, no confing has been found. keep it that way.
    config = check_config_updates(config)
