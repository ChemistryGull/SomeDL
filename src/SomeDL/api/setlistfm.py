import requests
import traceback

import SomeDL.utils.console as console

PROXY_TOKEN = "DfsJfEhyRccfceqlpimCdLoPRnQKWnHrFSmx"
BASE_URL = "https://somedl-proxy.somedl-proxy.workers.dev"

def setlistfm_get_artist(artist_name):
    url = f"{BASE_URL}/search/artists?artistName={artist_name}&sort=relevance"
    headers = {"Accept": "application/json", "X-Proxy-Token": PROXY_TOKEN}
    try:
        response = requests.get(url, headers=headers).json()
    except Exception as e:
        traceback.print_exc()

    return response


def setlistfm_get_setlist(mbid, page):
    console.info(f"Setlist API Request for artist with mbid {mbid}, on setlist page {page}")
    if not mbid:
        return jsonify({"error": "mbid is required"}), 400
    if not page:
        page = 1
        console.info("No page requested. Defaulting to 1")

    url = f"{BASE_URL}/artist/{mbid}/setlists?p={page}"
    headers = {"Accept": "application/json", "X-Proxy-Token": PROXY_TOKEN}


    try:
        response = requests.get(url, headers=headers).json()
    except Exception as e:
        # print("Error wh")
        traceback.print_exc()


    return response
    
