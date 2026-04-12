import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import requests

import SomeDL.utils.console as console
from SomeDL.utils.config import CONFIG_PATH

VERSION = "1.3.0"
CACHE_TTL_HOURS = 24
VERSION_CACHE_PATH = Path(CONFIG_PATH).with_name("somedl_version_cache.json")


def read_cache():
    # --- Return cached version string if fresh (< 24h), else None
    try:
        with open(VERSION_CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("current_version") != VERSION:  # invalidate on local version change
            return None
        cached_at = datetime.fromisoformat(data["cached_at"])
        age_hours = (datetime.now(timezone.utc) - cached_at).total_seconds() / 3600
        if age_hours < CACHE_TTL_HOURS:
            return data["latest_version"]
    except Exception:
        pass 
    return None


def write_cache(latest_version):
    # --- Write the latest version and current timestamp to the cache file
    try:
        data = {
            "latest_version": latest_version,
            "current_version": VERSION,
            "cached_at": datetime.now(timezone.utc).isoformat(),
        }
        console.debug("Writing somedl_version_cache.json")
        VERSION_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(VERSION_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass  # Just igronre if read-only filesystem, permissions, etc



def check_latest_version(print_version):
    # --- Check pypi for latest version (cached for 24 hours)
    try:
        latest_version = read_cache()

        if latest_version is None:
            url = "https://pypi.org/pypi/somedl/json"
            response = requests.get(url, timeout=3)
            response.raise_for_status()
            data = response.json()
            latest_version = data["info"]["version"]
            write_cache(latest_version)

        if not latest_version == VERSION:
            print()
            print(f"SomeDL v{VERSION}. A newer version is available: {latest_version}")
            print("If you installed SomeDL with pip, run the following command to update:")
            print("  python -m pip install --upgrade somedl")
        elif print_version:
            print()
            print(f"SomeDL v{VERSION}. You are up to date.")
        else:
            console.debug(f"SomeDL v{VERSION}. You are up to date.")

    except Exception as e:
        console.error(f"Could not check PyPI for updates: {e}")

