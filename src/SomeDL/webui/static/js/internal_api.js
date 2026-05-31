// === Adding item (webui->server ===)
async function dl_refresh() {
	const res = await fetch("/status");
	const data = await res.json();

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
    const item = document.getElementById("inp-downloader").value.split(",");
    document.getElementById("inp-downloader").value = "";
    console.log("searching for: " + item)
    var response = await fetch("/add", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({item})
    });


    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        return null; // or throw, or retry?
    }

    var data = await response.json()

    add_downloader_field_item(data.song_list)

}

async function add_list(list) {
    console.log("searching for: " + list)
    var response = await fetch("/add", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"item": list})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        return null; // or throw, or retry?
    }

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

    return data;
}


// === Controls ===
async function req_pause_download() {
    console.log("--- pause_download")
    var response = await fetch("/pause-download");

    if (!response.ok) {
        console.error("pause_download failed with:", response.status);
        return null; // or throw, or retry?
    }
}

async function req_resume_download() {
    console.log("--- resume_download")
    var response = await fetch("/resume-download");

    if (!response.ok) {
        console.error("resume_download failed with:", response.status);
        return null; // or throw, or retry?
    }
}

async function req_clear_queue() {
    console.log("--- clear_queue")
    var response = await fetch("/clear-queue");

    if (!response.ok) {
        console.error("clear_queue failed with:", response.status);
        return null; // or throw, or retry?
    }
}

async function req_remove_item(somedl_id) {
    console.log("--- remove_item")
    var response = await fetch("/remove-item", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({somedl_id: somedl_id})
    });

    if (!response.ok) {
        console.error("req_remove_item failed with:", response.status);
        return null; // or throw, or retry?
    }
}


// === Youtube ===
async function yt_search_download(url, target, artist_presets) {
    if (target) {
        flying_download_button(target);
    }
    console.log("searching for: " + url)
    var response = await fetch("/yt-download", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"url": url, "artist_presets": artist_presets})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        return null; // or throw, or retry?
    }

    var data = await response.json()
    
    add_downloader_field_item(data.song_list)
}

async function yt_search_req(search_query, filter) {
    console.log("--- Requesting yt search")
    var response = await fetch("/yt-search", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"search_query": search_query, "filter": filter})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        return null; // is handled in ytsearch.js
    }

    return data = await response.json()
}

async function yt_get_album_req(album_id) {
    console.log("--- Requesting album lookup by id")
    var response = await fetch("/yt-get-album", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"album_id": album_id})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        return null; // is handled in ytsearch.js
    }

    return data = await response.json()
}

async function yt_get_album_browse_id_req(album_id, return_album_data = false) {
    console.log("--- Requesting album lookup by id")
    response = await fetch("/yt-get-album-browse-id", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"album_id": album_id, "return_album_data": return_album_data})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        return null; // is handled in ytsearch.js
    }

    return data = await response.json()
}

async function yt_get_artist_req(artist_id) {
    console.log("--- Requesting artist lookup by id")
    response = await fetch("/yt-get-artist", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"artist_id": artist_id})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        return null; // is handled in ytsearch.js
    }

    return data = await response.json()
}


// === Setlist ===
async function setlist_artist_req(search_query) {
    console.log("--- Requesting setlist artist search")
    response = await fetch("/setlist-artist", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"search_query": search_query})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        return null; // or throw, or retry?
    }

    var data = await response.json()
    return data
}

async function setlist_get_req(mbid, page) {
    console.log("--- Requesting setlist artist search")
    var response = await fetch("/setlist-mbid", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"mbid": mbid, "page": page})
    });

    if (!response.ok) {
        console.error("Search failed with status:", response.status);
        return null; // or throw, or retry?
    }

    var data = await response.json()
    return data
}


// === Settings ===
async function settings_read() {
    console.log("--- settings_read")
    var response = await fetch("/settings-read", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({})
    });

    if (!response.ok) {
        console.error("Fetching settings failed with:", response.status);
        return null; // or throw, or retry?
    }

    var data = await response.json()
    return data
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
    return data;
}

async function req_webui_config_save(webui_settings) {
    console.log("--- webui-save-config")

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