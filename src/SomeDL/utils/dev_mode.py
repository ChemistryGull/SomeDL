# Only used in testing to store API responses to spare the API servers
import json
import os
import time
import base64
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock

FIXTURES_DIR = Path("/home/chemgull/Documents/Coding/Python/SomeDL/tests/mock_data/")
_call_counts = {}

def _is_json(response):
    content_type = response.headers.get("Content-Type", "")
    return "application/json" in content_type or "text/" in content_type

# def _next_path(key: str) -> Path:
#     n = _call_counts.get(key, 0)
#     _call_counts[key] = n + 1
#     safe = key.replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "_").replace("https://", "").replace("http://", "")[:80]
#     return FIXTURES_DIR / f"{safe}__{n}.json"

def _to_path(key: str) -> Path:
    safe = (key.replace("https://", "").replace("http://", "")
               .replace("/", "_").replace("?", "_").replace("&", "_")
               .replace("=", "_").replace(" ", "_"))[:120]
    return FIXTURES_DIR / f"{safe}.json"

def _save(path, data):
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))

def _load(path):
    if not path.exists():
        raise FileNotFoundError(f"No stored data at {path}, run store_data first")
    return json.loads(path.read_text())


def _yt_key(endpoint: str, body: dict) -> str:
    # use the full body as key so continuation tokens get their own cache entry
    body_hash = hashlib.md5(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]
    label = body.get('query') or body.get('browseId') or body.get('videoId') or 'x'
    safe_label = str(label).replace("/", "_").replace(" ", "_")[:40]
    return f"yt__{endpoint}__{safe_label}__{body_hash}"


# --- use this:
def run_with_data_storage(timer = 0):
    """Replay from disk, fetch and store if not cached yet."""
    from ytmusicapi import YTMusic
    import requests as real_requests

    real_get = real_requests.get
    real_yt_send = YTMusic._send_request

    def playback_get(url, **kwargs):
        path = _to_path(url)
        if not path.exists():
            print(f"  [CACHE MISS] fetching {url}")
            response = real_get(url, **kwargs)
            if _is_json(response):
                _save(path, {"type": "json", "url": url, "status_code": response.status_code, "body": response.json()})
            else:
                _save(path, {"type": "binary", "url": url, "status_code": response.status_code, "body": base64.b64encode(response.content).decode()})
            return response
        
        data = _load(path)
        mock = MagicMock()
        mock.status_code = data["status_code"]
        time.sleep(timer)
        if data["type"] == "json":
            mock.json.return_value = data["body"]
            mock.content = data["body"].encode() if isinstance(data["body"], str) else json.dumps(data["body"]).encode()
        else:
            mock.content = base64.b64decode(data["body"])
            mock.json.side_effect = Exception("Not a JSON response")
        return mock

    # def playback_yt_send(self, endpoint, body, *args):
    #     key = f"yt__{endpoint}__{body.get('query') or body.get('browseId') or body.get('videoId') or 'x'}"
    #     path = _to_path(key)
    #     if not path.exists():
    #         print(f"  [CACHE MISS] fetching yt {endpoint}")
    #         response = real_yt_send(self, endpoint, body)
    #         _save(path, {"endpoint": endpoint, "response": response})
    #         return response
        
    #     return _load(path)["response"]

    def playback_yt_send(self, *args):
        endpoint, body = args[0], args[1]
        key = _yt_key(endpoint, body)
        path = _to_path(key)
        if not path.exists():
            print(f"  [CACHE MISS] fetching yt {endpoint} / {key}")
            response = real_yt_send(self, *args)
            _save(path, {"endpoint": endpoint, "response": response})
            return response
        time.sleep(timer)
        return _load(path)["response"]

    patch("requests.get", playback_get).start()
    patch.object(YTMusic, "_send_request", playback_yt_send).start()
    print("\033[30;43m!!! DEBUG MODE: use_stored_data: replaying from", FIXTURES_DIR, "(fetches & caches on miss)\033[0m")
