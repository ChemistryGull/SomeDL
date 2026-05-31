import queue
import threading
import time
import base64
import hashlib
import json
import webbrowser
import logging

from flask import Flask, render_template, request, jsonify, Response
from waitress import serve

from SomeDL.core.processor import process_song_list_concurrent
from SomeDL.core.input_parser import generateSongList
from SomeDL.api.setlistfm import setlistfm_get_artist, setlistfm_get_setlist
import SomeDL.utils.console as console
from SomeDL.utils.config import config, change_configs, deep_update_config, generate_config, webui_config_load, webui_config_save
from SomeDL.api.ytmusic import yt
from SomeDL.utils.version import VERSION


# Replace default logging to make it work with rich (everything is put into console.webui(), as its only flask/werkzeug/waitress returning logging logs here)
class RichSafeHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        console.webui(msg)

        # Filter unwanted logs
        # if "GET /status" in msg:
        #     return
        # if "This is a development server." in msg:
        #     return
        # if "Press CTRL+C to quit" in msg:
        #     return
        # if "Debug mode:" in msg:
        #     return
        # Print safely via Rich
        # console.log(f'[white]{msg}[/]')

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichSafeHandler()]
)


app = Flask(__name__)

# === Main lists and queues ===

stop_event = threading.Event()

song_list_queue: queue.Queue = queue.Queue()
metadata_success_list: list = []
failed_list: list = []
already_downloaded_list: list = []
yt_dl_lock = threading.Lock()



# ### HTTP endpoints (webui->server) ### #

# === Download ===
@app.route("/status")
def get_status():
    answer = {
        "active_items": console.active_items,
        "finished_items": console.finished_item_ids,
        "items_in_queue": song_list_queue.qsize()
    } 
    return jsonify(answer)

@app.route("/get-queue")
def get_queue():
    return jsonify({
        "active": console.active_items,
        "queue": list(song_list_queue.queue)}
    )

@app.route("/shutdown", methods=["POST"])
def shutdown():
    stop_event.set()
    return jsonify({"ok": True})

@app.route("/add", methods=["POST"])
def add():
    data = request.json
    input_list = data.get("item")
    console.webui(f'Downloading songs: {input_list}')
    if not input_list:
        return jsonify({"error": "No item"}), 400

    songs_list = generateSongList(input_list)

    for item in songs_list:
        song_list_queue.put(item)

    return jsonify({"ok": True, "song_list": songs_list})

@app.route("/get-version")
def get_version():
    return {"v": VERSION}

@app.route("/get-history")
def get_history():
    console.webui(f'Fetching download history')
    answer = {
        "metadata_success_list": metadata_success_list,
        "failed_list": failed_list,
        "already_downloaded_list": already_downloaded_list
    }
    return jsonify(answer)


# === Controls ===
@app.route("/pause-download")
def pause_download():
    console.webui("Pausing download")
    console.pause_event.clear()
    return jsonify({"ok": True})

@app.route("/resume-download")
def resume_download():
    console.webui("Resuming download")
    console.pause_event.set()
    return jsonify({"ok": True})

@app.route("/clear-queue")
def clear_queue():
    console.webui("Clearing download queue")
    # --- Pause processing
    is_running = console.pause_event.is_set()
    console.pause_event.clear()
    
    # --- Drain queue
    try:
        while True:
            song_list_queue.get_nowait()
            song_list_queue.task_done()
    except queue.Empty:
        pass

    # --- Continue processing (to download the remaining ones)
    if is_running:
        console.pause_event.set()

    return jsonify({"ok": True})

@app.route("/remove-item", methods=["POST"])
def remove_item():
    data = request.json
    somedl_id = data.get("somedl_id")
    console.webui(f'Removing queue item with ID: {somedl_id}')

    if not (data):
        return jsonify({"error": "No settings from webui provided"}), 400

    # --- Pause processing
    is_running = console.pause_event.is_set()
    console.pause_event.clear()
    
    # --- Drain queue and add all items keep that are not the target somedl_id
    keep = []

    try:
        while True:
            item = song_list_queue.get_nowait()

            if str(item.get("somedl_id")) != str(somedl_id):
                keep.append(item)

            song_list_queue.task_done()

    except queue.Empty:
        pass

    # put remaining items back
    for item in keep:
        song_list_queue.put(item)

    # --- Continue processing (to download the remaining ones)
    if is_running:
        console.pause_event.set()

    return jsonify({"ok": True})


# === Youtube ===
@app.route("/yt-download", methods=["POST"])
def yt_download():
    data = request.json
    url = data.get("url")
    artist_presets = data.get("artist_presets")

    with yt_dl_lock: # --- Wait until the previous request is finished
        console.webui(f'Downloading {url}')
        if not url:
            return jsonify({"error": "No item"}), 400

        if artist_presets:
            orig_include_singles = config["download"]["include_singles"]
            orig_include_other_artists = config["download"]["include_other_artists"]
            config["download"]["include_singles"] = artist_presets.get("singles")
            config["download"]["include_other_artists"] = artist_presets.get("other")
            
        songs_list = generateSongList([url])

        if artist_presets:
            config["download"]["include_singles"] = orig_include_singles
            config["download"]["include_other_artists"] = orig_include_other_artists

        for item in songs_list:
            song_list_queue.put(item)

        # console.printj(list(song_list_queue.queue))

        return jsonify({"ok": True, "song_list": songs_list})

@app.route("/yt-search", methods=["POST"])
def yt_search():
    data = request.json
    search_query = data.get("search_query")
    search_filter = data.get("filter")
    console.webui(f'YT searching: "{search_query}"')
    if not (search_query and search_filter):
        return jsonify({"error": "No search_query or search_filter"}), 400

    
    try:
        search_results = yt.search(search_query, filter=search_filter)
    except Exception as e:
        console.warning("ytmusicapi error")
        return jsonify({"error": "ytmusicapi error"}), 503


    return jsonify({"ok": True, "result": search_results})

@app.route("/yt-get-album", methods=["POST"])
def yt_get_album():
    data = request.json
    album_id = data.get("album_id")
    console.webui(f'YT fetching album: {album_id}')
    if not album_id:
        return jsonify({"error": "No album_id"}), 400

    try:
        search_results = yt.get_playlist(album_id)
    except Exception as e:
        console.warning("ytmusicapi error")
        return jsonify({"error": "ytmusicapi error"}), 503

    return jsonify({"ok": True, "result": search_results})

@app.route("/yt-get-album-browse-id", methods=["POST"])
def yt_get_album_browse_id():
    data = request.json
    album_id = data.get("album_id")
    console.webui(f'YT fetching album: {album_id}')
    if not album_id:
        return jsonify({"error": "No album_id"}), 400

    try:
        album_results = yt.get_album(album_id)
        search_results = yt.get_playlist(album_results.get("audioPlaylistId"), limit=None)
    except Exception as e:
        console.warning("ytmusicapi error")
        return jsonify({"error": "ytmusicapi error"}), 503

    if data.get("return_album_data"):
        # --- If wanted, also returns the album result data
        return jsonify({"ok": True, "result": search_results, "album_data": album_results})
    else:
        return jsonify({"ok": True, "result": search_results})
 
@app.route("/yt-get-artist", methods=["POST"])
def yt_get_artist():
    data = request.json
    artist_id = data.get("artist_id")
    console.webui(f'YT fetching artist: {artist_id}')
    if not artist_id:
        return jsonify({"error": "No artist_id"}), 400

    try:
        artist_result = yt.get_artist(artist_id)
    except Exception as e:
        console.error("Artist search returned no results. Skipping this artist. Error info:")
        console.error(e)
        return jsonify({"error": "Interal exception in yt-get-artist"}), 400

    # console.printj(artist_result)

    if artist_result.get("related"):
        artist_result.pop("related") # --- Remove unneccessary data

    artist_name = artist_result.get("name")
    console.webui(f'Looking up discography of: "{artist_name}"')


    albums_browseId = artist_result.get("albums", {}).get("browseId")
    albums_params = artist_result.get("albums", {}).get("params")
    singles_browseId = artist_result.get("singles", {}).get("browseId")
    singles_params = artist_result.get("singles", {}).get("params")


    # === Album ===
    
    # --- Check if "more" button exists in UI, if yes, fetch the data that is reachable with the more button
    if albums_browseId and albums_params:
        console.debug("\"more\" button found, fetching more data")
        artist_albums_result = yt.get_artist_albums(albums_browseId, albums_params)
    else:
        console.debug("No \"more\" button, using initial fetched data.")
        artist_albums_result = artist_result.get("albums", {}).get("results", [])



    # --- Set this modified data into the response
    artist_result.get("albums", {})["results"] = artist_albums_result


    # === Singles ===

    # --- Check if "more" button exists in UI, if yes, fetch the data that is reachable with the more button
    if singles_browseId and singles_params:
        console.debug("\"more\" button found, fetching more data")
        artist_singles_result = yt.get_artist_albums(singles_browseId, singles_params)
    else:
        console.debug("No \"more\" button, using initial fetched data.")
        artist_singles_result = artist_result.get("singles", {}).get("results", [])

    
    artist_result.get("singles", {})["results"] = artist_singles_result

    
    


    return jsonify({"ok": True, "result": artist_result})


# === Setlist ===
@app.route("/setlist-artist", methods=["POST"])
def setlist_artist():
    data = request.json
    search_query = data.get("search_query")
    console.webui(f'Looking up artist on setlist.fm "{search_query}"')
    if not (search_query):
        return jsonify({"error": "No search_query"}), 400

    search_results = setlistfm_get_artist(search_query)
    return search_results

@app.route("/setlist-mbid", methods=["POST"])
def setlist_mbid():
    data = request.json
    mbid = data.get("mbid")
    page = data.get("page")
    console.webui(f'Fetching setlist data: {mbid}, page {page}')
    if not (mbid):
        return jsonify({"error": "No search_query"}), 400

    setlist_result = setlistfm_get_setlist(mbid, page)
    return setlist_result


# === Settings ===
@app.route("/settings-read", methods=["POST"])
def settings_read():
    with yt_dl_lock:
        return config

@app.route("/settings-apply", methods=["POST"])
def settings_apply():
    data = request.json
    settings = data.get("settings")
    update_active = data.get("update_active")
    if not (data):
        return jsonify({"error": "No settings from webui provided"}), 400

    with yt_dl_lock: # --- avoid writing the config at the same time yt-download is running (yt-download may change the config)
        console.webui(f'Saving settings')

        reformatted_settings = [
            [section, key, value]
            for section, values in settings.items()
            for key, value in values.items()
        ]

        change_configs(reformatted_settings)

        if update_active:
            # --- Update all config options in place
            console.webui(f'Applying settings')
            deep_update_config(settings)

        return jsonify({"ok": True})


# === WebUI configs ===
@app.route("/webui-load-config")
def req_webui_load_config():
    answer = webui_config_load()

    # --- Manual response instead of jsonify to avoid alphabetic ordering
    return Response(
        json.dumps(answer),
        mimetype="application/json"
    )

@app.route("/webui-save-config", methods=["POST"])
def req_webui_save_config():
    data = request.json
    webui_settings = data.get("webui_settings")
    if not (webui_settings):
        return jsonify({"error": "No webui settings from webui provided"}), 400

    webui_config_save(webui_settings)
    
    return jsonify({"ok": True})


# === Serve main HTML page ===
@app.route("/")
def index():
    return render_template("index.html")  # Flask looks in templates/


# === Main stuff ===
def start_server():
    # app.run(host=config["webui"]["host"], port=config["webui"]["port"], debug=False, use_reloader = False)
    serve(app, host=config["webui"]["host"], port=config["webui"]["port"])

def start_backend():
    process_song_list_concurrent(song_list_queue, False, metadata_success_list, failed_list, already_downloaded_list)

def start_webui():
    # --- Developement servers:
    # app.run(host=config["webui"]["host"], port=config["webui"]["port"], debug=True, use_reloader = True)
    # serve(app, host=config["webui"]["host"], port=config["webui"]["port"])
    # return

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    if config["webui"]["open_browser"]:
        if config["webui"]["browser"]:
            browser = webbrowser.get(config["webui"]["browser"])
            browser.open(f'http://127.0.0.1:{config["webui"]["port"]}/')
        else:
            webbrowser.open(f'http://127.0.0.1:{config["webui"]["port"]}/')

    time.sleep(1)

    t2 = threading.Thread(target=start_backend, daemon=True)
    t2.start()

    # --- The main download logic threads
    # process_song_list_concurrent(song_list_queue, False, metadata_success_list, failed_list, already_downloaded_list)

    try:
        stop_event.wait()
        console.live_display.stop()
        print("\nShutting down SomeDL")
    except KeyboardInterrupt:
        console.live_display.stop()
        print("\nCtrl+C pressed, Shutting down SomeDL")

# def start_webui_webview():
#     # app.run(host=config["webui"]["host"], port=config["webui"]["port"], debug=True, use_reloader = True)
#     #serve(app, host="127.0.0.1", port=5001)

#     # return


#     # start web UI in background (maybe start downloader in thread instead??)
#     # t = threading.Thread(target=start_server, daemon=True)
#     # t.start()
#     print("")
#     print("Starting Web UI on http://127.0.0.1:5000")
#     time.sleep(1)

#     # further code...
#     t2 = threading.Thread(target=start_backend, daemon=True)
#     t2.start()

#     # process_song_list_concurrent(song_list_queue, False, metadata_success_list, failed_list, already_downloaded_list)


#     # webview.create_window('Hello world', 'http://127.0.0.1:5000')
#     webview.create_window('Hello world', app)
#     webview.start(gui='gtk')
#     print("####END###")

#     # t.join()
#     # t2.join()


#     # try:
#     #     stop_event.wait()
#     # except KeyboardInterrupt:
#     #     print("\nCtrl+C pressed, exiting.....")
