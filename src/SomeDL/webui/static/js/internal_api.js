// === Adding item (webui->server ===)
async function dl_refresh() {
	const res = await fetch("/status");
	const data = await res.json();
    console.log(data);
    
    return data;
}

async function refresh_queue() {
	const res = await fetch("/get-queue");
	const data = await res.json();

    return data;
}

async function req_shutdown() {
    console.log("--- Shutting down server")
    var response = await fetch("/shutdown", {
        method: "POST"
    });

    if (!response.ok) {
        console.error("Shutdown failed with:", response.status);
        alert("Shutdown failed! Please manually terminate SomeDL from the commandline (Ctrl+C)")
        return null; // or throw, or retry?
    }
    
    window.location.reload();
    return
}

async function add_item() {

    const input_list = document.getElementById("inp-downloader").value.split(",").map(s => s.trim()).filter(s => s.length > 0);
    document.getElementById("inp-downloader").value = "";
    console.log("--- add_item: searching for: " + input_list)

    loader.start()

    var response = await fetch("/add", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({input_list})
    });


    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        loader.stop("Error: Search failed with status: " + response.status)

        return null; // or throw, or retry?
    }

    loader.stop()
    var data = await response.json()

    add_downloader_field_item(data.song_list)

}

async function add_list(list) {
    console.log("--- add_list: searching for: " + list)
    loader.start()

    var response = await fetch("/add", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"input_list": list})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        loader.stop("Error: Search failed with status: " + response.status)

        return null; // or throw, or retry?
    }

    loader.stop()
    var data = await response.json()

    add_downloader_field_item(data.song_list)

}

async function get_version() {
	const res = await fetch("/get-version");
	const data = await res.json();
    console.log(data);
    return data;
}

async function refresh_history_req() {
	const res = await fetch("/get-history");
	const data = await res.json();
    console.log(data);
    
    return data;
}


async function req_open_file(path) {
    loader.start();
    console.log("opening file" + path)
    var response = await fetch("/open-file", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({path})
    });

    if (!response.ok) {
        console.error("Opening file failed with:", response.status);
        if (response.status == 404) {
            loader.stop("Error: File not found.");
        } else {
            loader.stop("Error: Opening file failed with: " + response.status);
        }
        return null; // or throw, or retry?
    }
    loader.stop();
}

async function req_get_download_report() {
    loader.start();
    var response = await fetch("/get-download-report", {method: "GET"});
	const data = await response.json();
    console.log(data);
    if (!response.ok) {
        console.error("Failed to generate download report:", response.status);
        loader.stop("Error: Failed to generate download report: " + response.status);
        return null;
    }

    loader.stop();
    return data.html;
}

async function req_clear_download_history() {
    loader.start();
    var response = await fetch("/clear-download-history", {
        method: "POST"
    });

    if (!response.ok) {
        console.error("Clearing history failed with:", response.status);
        loader.stop("Error: Failed to clear download history. You can manually clear the download history by restarting the server: " + response.status);
        return null;
    }
    loader.stop();   
    return
}



// === Controls ===
async function req_pause_download() {
    loader.start();
    console.log("--- pause_download")
    var response = await fetch("/pause-download", {method: "POST"});

    if (!response.ok) {
        console.error("pause_download failed with:", response.status);
        loader.stop("Error: Pause download failed with: " + response.status);
        return null; // or throw, or retry?
    }
    loader.stop();
}

async function req_resume_download() {
    loader.start();
    console.log("--- resume_download")
    var response = await fetch("/resume-download", {method: "POST"});

    if (!response.ok) {
        console.error("resume_download failed with:", response.status);        
        loader.stop("Error: Resume download failed with: " + response.status);
        return null; // or throw, or retry?
    }
    loader.stop();
}

async function get_downloader_state() {
    console.log("--- get_downloader_state")
    var response = await fetch("/get-downloader-state", {method: "GET"});

    if (!response.ok) {
        console.error("Failed getting downloader state with:", response.status);
        return null; // or throw, or retry?
    }
    var data = await response.json();
    return data;
}

async function req_clear_queue() {
    loader.start();
    console.log("--- clear_queue")
    var response = await fetch("/clear-queue", {method: "POST"});

    if (!response.ok) {
        console.error("clear_queue failed with:", response.status);
        loader.stop("Error: Clearing queue failed with: " + response.status);
        return null; // or throw, or retry?
    }
    loader.stop();
}

async function req_remove_item(somedl_id) {
    loader.start();
    console.log("--- remove_item")
    var response = await fetch("/remove-item", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({somedl_id: somedl_id})
    });

    if (!response.ok) {
        console.error("req_remove_item failed with:", response.status);
        loader.stop("Error: Removing item failed with: " + response.status);
        return null; // or throw, or retry?
    }
    loader.stop();
}


// === Youtube ===
async function yt_search_download(url, target, artist_presets) {
    if (target) {
        flying_download_button(target);
    }
    console.log("searching for: " + url)
    loader.start();
    var response = await fetch("/yt-download", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"url": url, "artist_presets": artist_presets})
    });

    if (!response.ok) {
        console.error("Adding to download queue failed with status:", response.status);
        loader.stop("Error: Adding to download queue failed with status: " + response.status);
        return null; // or throw, or retry?
    }

    loader.stop();
    var data = await response.json()

    add_downloader_field_item(data.song_list)
}

async function yt_search_req(search_query, filter) {
    console.log("--- Requesting yt search")
    loader.start();
    var response = await fetch("/yt-search", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"search_query": search_query, "filter": filter})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        loader.stop("Error: Search failed with status: " + response.status);
        return null; // is handled in ytsearch.js
    }
    loader.stop();
    const data = await response.json()    
    return data
}

async function yt_get_album_req(album_id) {
    console.log("--- Requesting album lookup by id")
    loader.start();
    var response = await fetch("/yt-get-album", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"album_id": album_id})
    });

    if (!response.ok) {
        console.error("Requesting album failed with status:", response.status);
        loader.stop("Error: Requesting album failed with status: " + response.status);
        return null; // is handled in ytsearch.js
    }
    loader.stop();
    const data = await response.json()
    return data
}

async function yt_get_album_browse_id_req(album_id, return_album_data = false) {
    console.log("--- Requesting album lookup by id")
    loader.start();
    var response = await fetch("/yt-get-album-browse-id", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"album_id": album_id, "return_album_data": return_album_data})
    });

    if (!response.ok) {
        console.error("Requesting album lookup failed with status:", response.status);
        loader.stop("Error: Requesting album lookup failed with status: " + response.status);
        return null; // is handled in ytsearch.js
    }
    loader.stop();
    const data = await response.json()
    return data
}

async function yt_get_artist_req(artist_id) {
    console.log("--- Requesting artist lookup by id: " + artist_id)
    loader.start();
    var response = await fetch("/yt-get-artist", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"artist_id": artist_id})
    });

    if (!response.ok) {
        console.error("Requesting artist lookup failed with status:", response.status);
        loader.stop("Error: Requesting artist lookup failed with status: " + response.status);
        return null; // is handled in ytsearch.js
    }
    loader.stop();
    const data = await response.json()
    return data
}


// === Setlist ===
async function setlist_artist_req(search_query) {
    console.log("--- Requesting setlist artist search")
    loader.start();
    var response = await fetch("/setlist-artist", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"search_query": search_query})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        if (response.status == 504) {
            loader.stop("Error: Requesting setlist on setlist.fm timed out");
        } else {
            loader.stop("Error: Searching for artist on setlist.fm failed with status: " + response.status);
        }
        return null; // or throw, or retry?
    }
    
    loader.stop();
    var data = await response.json()
    
    return data.result
}

async function setlist_get_req(mbid, page) {
    console.log("--- Requesting setlist")
    loader.start();
    var response = await fetch("/setlist-mbid", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"mbid": mbid, "page": page})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        if (response.status == 504) {
            loader.stop("Error: Requesting setlist on setlist.fm timed out");
        } else {
            loader.stop("Error: Requesting setlist on setlist.fm failed with status: " + response.status);
        }
        return null; // or throw, or retry?
    }

    loader.stop();
    var data = await response.json()

    return data.result
}


// === Settings ===
async function settings_read() {
    console.log("--- settings_read")
    var response = await fetch("/settings-read", {method: "GET"});

    if (!response.ok) {
        console.error("Fetching settings failed with:", response.status);
        return null; // or throw, or retry?
    }

    var data = await response.json()
    
    return data.config
}

async function settings_apply(settings, update_active) {
    console.log("--- settings_apply")
    
    var response = await fetch("/settings-apply", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({settings: settings, update_active: update_active})
    });

    if (!response.ok) {
        console.error("Setting settings failed with:", response.status);
        return null; // or throw, or retry?
    }

    var data = await response.json()
    return data
}


// === WebUI configs ===
async function req_webui_config_load() {
    console.log("--- webui-load-config")
    var response = await fetch("/webui-load-config");

    if (!response.ok) {
        console.error("webui-load-config failed with:", response.status);
        return null; // or throw, or retry?
    }

    var data = await response.json()

    console.log(data);
    
    return data;
}

async function req_webui_config_save(webui_settings) {
    console.log("--- webui-save-config")
    console.log({webui_settings});
    
    var response = await fetch("/webui-save-config", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({webui_settings})
    });

    if (!response.ok) {
        console.error("webui-save-config failed with:", response.status);
        return null; // or throw, or retry?
    }

}