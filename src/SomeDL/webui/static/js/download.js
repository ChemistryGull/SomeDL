// === Controls ===

// refresh_queue_items()

var download = {
    async clear_queue () {
        await req_clear_queue();
        refresh_queue_items();
    },
    pause () {
        req_pause_download();
        document.querySelectorAll(".download-btn-pause").forEach(el => el.style.display = "none");
        document.querySelectorAll(".download-btn-resume").forEach(el => el.style.display = "flex");
    },
    resume () {
        req_resume_download();
        document.querySelectorAll(".download-btn-pause").forEach(el => el.style.display = "flex");
        document.querySelectorAll(".download-btn-resume").forEach(el => el.style.display = "none");

    },
    async remove (somedl_id) {
        await req_remove_item(somedl_id);
        refresh_queue_items();
    },
    shutdown () {
        alert_box('Shut down SomeDL?', `
        <p>Do you want to turn off the server? Active downloads will be cancelled.</p>
        <div class="popup-button-box">
            <button class="ui-button ui-button-small popup-exit"" onclick="req_shutdown()">OK</button>
            <button class="ui-button ui-button-small popup-exit">Cancel</button>
        </div>  
        `)
    }
}


// === Download area ===

function add_downloader_field_item(song_list) {
    console.log("add_downloader_field_item");
    console.log(song_list);

    var downloader_field = document.getElementById("downloader-field");

    for (let i = 0; i < song_list.length; i++) {
        const song = song_list[i];

        song_title = song.text_query || `${song.artist_name} - ${song.song_title}`;
        
        new_item_str = new_item_template(song.somedl_id, song_title)

        downloader_field.insertAdjacentHTML("beforeend", new_item_str);
        
    }

    
    dl_status_active = true;
}

async function refresh_queue_items() {
    var data = await refresh_queue()
    console.log("=== Refreshing download queue ===");
    console.log(data);

    // --- rename old field
    var old_field = document.getElementById("downloader-field");
    old_field.id = "downloader-field-old";
    var scroll_pos = old_field.scrollTop;

    // --- create new hidden field from old field
    var new_field = old_field.cloneNode(true);
    new_field.id = "downloader-field";
    new_field.classList.add("downloader-field", "dl-field-no-transition");
    new_field.style.visibility = "hidden";
    new_field.querySelectorAll('.active').forEach(el => el.remove()); // --- if called from download.clear_queue(), keep the already downloaded items, only refresh the others (new queue)

    // --- Add active elements
    for (const [key, value] of Object.entries(data.active)) {
        song_title = value.text.split(/ (.+)/)[1]

        new_item_str = new_item_template(key, song_title)

        new_field.insertAdjacentHTML("beforeend", new_item_str);
    }

    // --- Add field to DOM
    old_field.parentNode.insertBefore(new_field, old_field.nextSibling);

    // --- Add queue elements
    add_downloader_field_item(data.queue)
    await dl_update_status()

    // --- remove old field and make new field visible
    old_field.remove()
    new_field.scrollTop = scroll_pos;

    new_field.style.visibility = "";

    // --- Force a DOM draw
    void new_field.offsetHeight;

    // setTimeout(() => {
    //     // --- Enable transition after items have been drawn
    //     downloader_field.classList.remove("dl-field-no-transition");
    // }, 100);
    // --- Enable transitions again
    new_field.classList.remove("dl-field-no-transition");
   
    
}

function new_item_template(somedl_id, title) {
    return `<div class="dl-item active dl-queue-item" data-id="${somedl_id}">
                <div class="dl-item-dlbar dl-queue"></div>
                <div class="dl-item-title">${title}</div>
                <div class="dl-item-status">Queued</div>
                <div class="dl-item-remove" onclick="download.remove('${somedl_id}')">${icons.trash}</div>
            </div>`
}


async function dl_update_status() {
    console.log(dl_status_active);

    if (dl_status_active == 0) return; // --- skip if no download is active
    
	var data = await dl_refresh()
 
    // in_queue_nr = Object.keys(data.items_in_queue).length;
    var active_downloads_nr = Object.keys(data.active_items).length;
    var finished_downloads_nr = Object.keys(data.finished_items).length;
    update_download_tracker(active_downloads_nr + data.items_in_queue, finished_downloads_nr);

    // console.log(data);
    // console.log(data.items_in_queue + " | " + active_downloads_nr);
    
    if (data.items_in_queue == 0 && active_downloads_nr == 0) {
        dl_status_active = false;
    }



    if (active_page != "download") return; // --- Skip if window is not in focus


    document.querySelectorAll(".dl-item.active").forEach((node) => {
        var somedl_id = node.dataset.id

        var status_node = node.querySelector(".dl-item-status");
        var dl_bar_node = node.querySelector(".dl-item-dlbar"); 

        if (data.active_items[somedl_id]) {
            // dl_bar_node.style.display = "block";
            //         "text": "1/2 The Warning - MORE",

            node.querySelector(".dl-item-title").innerHTML = data.active_items[somedl_id].text.split(/ (.+)/)[1];


            dl_bar_node.classList.remove("dl-queue");
            node.classList.remove("dl-queue-item");

            var status_data = data.active_items[somedl_id].data;


            if (status_data["albumart"]) {
                status_node.innerHTML = "Downloading"
                dl_bar_node.style.right = "0";
            
            } else if (status_data["downloading"]) {
                status_node.innerHTML = "Downloading"
                dl_bar_node.style.right = "20%";
            
            } else if (status_data["wait_queue"]) {
                status_node.innerHTML = "Waiting for download"
                dl_bar_node.style.right = "50%";

            } else if (status_data["get_lyrics"]) {
                status_node.innerHTML = "Fetching metadata"
                dl_bar_node.style.right = "60%";

            } else if (status_data["musicbrainz"]) {
                status_node.innerHTML = "Fetching metadata"
                dl_bar_node.style.right = "70%";
            
            } else if (status_data["deezer"]) {
                status_node.innerHTML = "Fetching metadata"
                dl_bar_node.style.right = "80%";

            } else if (status_data["album"]) {
                status_node.innerHTML = "Fetching metadata"
                dl_bar_node.style.right = "90%";

            }
            
        } else if (data.finished_items[somedl_id]) {
            dl_bar_node.style.display = "block";
            dl_bar_node.style.right = "0";

            node.removeAttribute("data-id");
            dl_bar_node.classList.remove("dl-queue");
            node.classList.remove("dl-queue-item");
            node.classList.replace("active", "dl-finished"); // --- dl-finished used in refresh_queue_items()

            switch (data.finished_items[somedl_id]) {
                case "success":
                    status_node.innerHTML = "Success"
                    dl_bar_node.style.background = "green";
                    // node.style.background = "green";
                    // status_node.style.color = "green";
                    // status_node.classList.add("dl-finished")
                    // status_node.style.background = "green";

                    break;
                case "download_disabled":
                    status_node.innerHTML = "Download disabled"
                    dl_bar_node.style.background = "darkgoldenrod";
                    // node.style.background = "darkgoldenrod";
                    // status_node.style.color = "darkgoldenrod";
                    // status_node.classList.add("dl-finished")
                    // status_node.style.background = "darkgoldenrod";

                    break;
                case "failed":
                    status_node.innerHTML = "Download failed"
                    dl_bar_node.style.background = "red";
                    // node.style.background = "red";
                    // status_node.style.color = "red";
                    // status_node.classList.add("dl-finished")
                    // status_node.style.background = "red";

                    break;
                case "already_downloaded":
                    status_node.innerHTML = "Already downloaded"
                    dl_bar_node.style.background = "blue";
                    // node.style.background = "blue";
                    // status_node.style.color = "blue";
                    // status_node.classList.add("dl-finished")
                    // status_node.style.background = "blue";

                    break;
                default:
                    status_node.innerHTML = "ERROR"
                    break;
            }
        }
       
    })
}

function update_download_tracker(active_nr, finished_nr) {
    document.getElementById("dl-tracker-queue").innerHTML = active_nr;
    document.getElementById("dl-tracker-fin").innerHTML = finished_nr;
}


