import requests

from SomeDL.utils.logging import log

VERSION = "1.0.0"

def check_latest_version(print_version):
    # --- Check pypi for latest version
    url = f"https://pypi.org/pypi/somedl/json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        latest_version = data["info"]["version"]
        if not latest_version == VERSION:
            print()
            print(f"SomeDL v{VERSION}. A newer version is available: {latest_version}")
        elif print_version:
            print()
            print(f'SomeDL v{VERSION}. You are up to date.')
        else:
            log.debug(f'SomeDL v{VERSION}. You are up to date.')
    except Exception as e:
        log.warning(f'Could not check PyPI for updates: {e}')
