// === YouTube Search ===

async function yt_search() {
    const search_query = document.getElementById("inp-yt-search").value;
    const filter = document.querySelector('input[name="type"]:checked')?.value;

    document.querySelectorAll('.yt-search-results-field:not(#yt-search-results-field)').forEach(el => el.remove()); // --- Remove all unused dom result divs to avoid buildup
    
    yt_search_results_field = document.getElementById("yt-search-results-field")

    yt_search_results_field.innerHTML = "Loading..."


    // const filter = "albums"
    console.log("searching for: " + search_query)
    var res = await yt_search_req(search_query, filter)

    if (!res) {
        yt_search_results_field.innerHTML =  "<p>Unexpected error. Please try again. If that doesn't help, try restarting SomeDL.</p>";
        return;
    }

    console.log(res.result);

    if (res.result.length == 0) {
        search_results_string = `<div>No results for "${search_query}". If you think thats a mistake, try restarting the application.</div>`;
    } else {
        search_results_string = ""
    }



    if (filter == "songs") {
        for (let i = 0; i < res.result.length; i++) {
            const element = res.result[i];
            
            album_art_url   = element.thumbnails[0]?.url;
            title           = element.title ?? "Song has no title";
            // artists_names   = (element.artists || []).map(a => a.name).join(", ");
            album_name      = element.album?.name ?? "Unknown album";
            album_id        = element.album?.id;
            duration        = element.duration;
            views           = element.views;
            video_id        = element.videoId;
            

            artists_names_arr = []
            for (let i = 0; i < element.artists.length; i++) {
                artist = element.artists[i];
                artists_names_arr.push(`<span onclick="yt_get_artist_content('${artist.id}')">${artist.name}</span>`)
            }
            artists_names = artists_names_arr.join(", ")

            search_results_string += `
                <div class="yt-search-item">
                    <div class="yt-search-coverart">
                        <img src="${album_art_url}" alt="Coverart">
                        <button class="yt-search-download-btn" onclick="yt_search_download('https://music.youtube.com/watch?v=${video_id}', this)">${icons.download()}</button>
                    </div>
                    <div class="yt-search-text">
                        <div class="yt-search-title" title="${title}">${title}</div>
                        <div class="yt-search-bottom">
                            <div class="yt-search-artist">${artists_names}</div>
                            <span class="yt-search-bottom-separator"> • </span>
                            <div class="yt-search-album" title="${album_name}"><span onclick="yt_get_album('${album_id}')">${album_name}</span></div>
                            <span class="yt-search-bottom-separator"> • </span>
                            <div class="yt-search-duration">${duration}</div>
                            <span class="yt-search-bottom-separator"> • </span>
                            <div class="yt-search-views">${views}</div>
                        </div>
                    </div>
                </div>`
            
        }
    } else if (filter == "albums") {
        for (let i = 0; i < res.result.length; i++) {
            const element = res.result[i];
            
            album_art_url   = element.thumbnails[0]?.url;
            title           = element.title ?? "Song has no title";
            // artists_names   = (element.artists || []).map(a => a.name).join(", ");
            type            = element.type;
            year            = element.year;
            playlist_id     = element.playlistId;
            browse_id       = element.browseId;

            artists_names_arr = []
            for (let i = 0; i < element.artists.length; i++) {
                artist = element.artists[i];
                artists_names_arr.push(`<span onclick="yt_get_artist_content('${artist.id}')">${artist.name}</span>`)
            }
            artists_names = artists_names_arr.join(", ")

            search_results_string += `
            <div class="yt-search-item-wrapper">
                <div class="yt-search-item">
                    <div class="yt-search-coverart">
                        <img src="${album_art_url}" alt="Coverart">
                        <button class="yt-search-download-btn" onclick="yt_search_download('https://music.youtube.com/browse/${browse_id}', this)">${icons.download()}</button>
                    </div>
                    <div class="yt-search-text">
                        <div class="yt-search-title yt-search-artist-album" onclick="yt_get_album('${browse_id}')" title="${title}">${title}</div>
                        <div class="yt-search-bottom">
                            <div class="yt-search-type">${type}</div>
                            <span class="yt-search-bottom-separator"> • </span>
                            <div class="yt-search-artist">${artists_names}</div>
                            <span class="yt-search-bottom-separator"> • </span>
                            <div class="yt-search-year">${year}</div>
                        </div>
                    </div>
                    <div class="yt-search-more" onclick="yt_get_album_items(this, '${playlist_id}', '${browse_id}')">${icons.chevron_right}</div>
                </div>
                <div class="yt-search-album-items"></div>
            </div>`
            
        }
    } else if (filter == "artists") {
        for (let i = 0; i < res.result.length; i++) {
            const element = res.result[i];
            
            album_art_url   = element.thumbnails[0]?.url;
            artist          = element.artist ?? "Unknown artist";
            type            = element.category;
            browse_id       = element.browseId;

            search_results_string += `
                <div class="yt-search-item">
                    <div class="yt-search-coverart">
                        <img src="${album_art_url}" alt="Coverart">
                        <button class="yt-search-download-btn" onclick="prompt_yt_download_artist('https://music.youtube.com/channel/${browse_id}', '${artist}')">${icons.download()}</button>
                    </div>
                    <div class="yt-search-text clickable" onclick="yt_get_artist_content('${browse_id}')">
                        <div class="yt-search-title" title="${artist}">${artist}</div>
                    </div>
                </div>`
            
        }
    }

    yt_search_results_field.innerHTML = search_results_string;
}

async function yt_get_artist_content(browse_id) {
    console.log(browse_id);

    // var data = await yt_get_artist_req("UCDcpm0VmhmPUFLCkbjqJ2AQ")
    // var data = await yt_get_artist_req("UCijF534Q4VFffUT-B4TFT9Q")
    var artist_data = await yt_get_artist_req(browse_id)
    if (!artist_data) {
        alert("Unexpected error. Please try again. If that doesn't help, try restarting SomeDL.");
        return;
    }

    // var data = test_artust_data.result
    var data = artist_data.result
    console.log(artist_data);
    console.log(data);


    var old_results_field = document.getElementById("yt-search-results-field")
    
    var history_id = old_results_field.className.match(/yt-search-results-field-history-(\d+)/);
    console.log(history_id);

    if (history_id) {
        var new_history_number = Number(history_id[1]) + 1
        var old_history_number = Number(history_id[1])
    } else {
        console.log("----- NO HIST ID!!!!!!");
        var new_history_number = 1
        var old_history_number = 0
    }

    old_results_field.removeAttribute('id');


    var yt_search_results_field = document.createElement("div");
    yt_search_results_field.id = "yt-search-results-field"
    yt_search_results_field.classList.add("yt-search-results-field")
    yt_search_results_field.classList.add("yt-search-results-field-history-" + new_history_number)


    

    var thumbnail       = data.thumbnails?.[2]?.url ?? data.thumbnails?.[1]?.url ?? data.thumbnails?.[0]?.url;
    var artist          = data.name;
    var description     = data.description

    if (description) {
        description = description.replace("\n", "<br><br>");
    } else {
        description = "";
    }
    

    var limit = 100;
    var cut_index = description.lastIndexOf(" ", limit);
    

    var description1    = description.substring(0, cut_index);
    var description2    = description.substring(cut_index);
    if (cut_index < 0) {
        description1 = description;
        description2 = "";
    }

    var html_description = ""

    console.log(description);
    console.log(description1);
    console.log(description2);
    
    
    if (description1.length > 0) {
        html_description += `
        <span>
            ${description1}
        </span>`
    }
    if (description2.length > 0) {
        html_description += `
        <span class="toggle_more_dots">...</span>
        <span class="toggle_more">
            ${description2}    
        </span>
        <span onclick="toggle_more_btn(this)" class="toggle_more_btn">
            MORE
        </span>`
    }




    search_results_string = `
        <div class="yt-search-artist-wrapper">
            <div class="yt-search-artist-header" style="background-image: url('${thumbnail}');">
                <div class="yt-search-artist-header-btns-wrapper">
                    <button class="ui-button" onclick="yt_search_return_btn('yt-search-results-field-history-${old_history_number}')">${icons.chevron_left}</button>
                    <button class="ui-button" title="Download all songs by artist" onclick="prompt_yt_download_artist('https://music.youtube.com/channel/${browse_id}', '${artist}')">${icons.download()}</button>
                </div>
                <div class="yt-search-artist-header-title">
                    <div class="yt-search-artist-name">${artist}</div>
                    <div class="yt-search-artist-desc">
                        ${html_description}
                    </div>
                </div>
            </div>


            <h3>Albums</h3>
            
            <div class="yt-search-artist-albums">
                This artist has not released any albums.
            </div>


            <h3>Singles</h3>

            <div class="yt-search-artist-singles">
                This artist has not released any singles or EPs.
            </div>

        </div>`;

    yt_search_results_field.innerHTML = search_results_string;


    // === Albums ===

    if (data.albums) {
        var yt_artist_albums = ""
   
        for (let i = 0; i < data.albums.results.length; i++) {
            const element = data.albums.results[i];
            
            album_art_url   = element.thumbnails[0]?.url;
            title           = element.title.trim() ?? "Song has no title";
            type            = element.type ?? "Album";
            year            = element.year ?? "";
            playlist_id     = element.playlistId;
            browse_id       = element.browseId;

            yt_artist_albums += `
            <div class="yt-search-item-wrapper yt-search-item-wrapper-artist">
                <div class="yt-search-item">
                    <div class="yt-search-coverart">
                        <img src="${album_art_url}" alt="Coverart">
                        <button class="yt-search-download-btn" onclick="yt_search_download('https://music.youtube.com/browse/${browse_id}', this)">${icons.download()}</button>
                    </div>
                    <div class="yt-search-text">
                        <div class="yt-search-title yt-search-artist-album" onclick="yt_get_album('${browse_id}')" title="${title}">${title}</div>
                        <div class="yt-search-bottom">
                            <div class="yt-search-type">${type}</div>
                            <span class="yt-search-bottom-separator"> • </span>
                            <div class="yt-search-year">${year}</div>
                        </div>
                    </div>
                    <div class="yt-search-more" onclick="yt_get_album_items(this, '${playlist_id}', '${browse_id}')">${icons.chevron_right}</div>
                </div>
                <div class="yt-search-album-items"></div>
            </div>`
            
        }

        yt_search_results_field.querySelector(".yt-search-artist-albums").innerHTML = yt_artist_albums;
    }

    

    // === Singles ===

    if (data.singles) {
        var yt_artist_singles = ""
   
        for (let i = 0; i < data.singles.results.length; i++) {
            const element = data.singles.results[i];
            
            album_art_url   = element.thumbnails[0]?.url;
            title           = element.title.trim() ?? "Song has no title";
            type            = element.type ?? "sth";
            year            = element.year ?? "";
            playlist_id     = element.playlistId;
            browse_id       = element.browseId;

            yt_artist_singles += `
            <div class="yt-search-item-wrapper yt-search-item-wrapper-artist">
                <div class="yt-search-item">
                    <div class="yt-search-coverart">
                        <img src="${album_art_url}" alt="Coverart">
                        <button class="yt-search-download-btn" onclick="yt_search_download('https://music.youtube.com/browse/${browse_id}', this)">${icons.download()}</button>
                    </div>
                    <div class="yt-search-text">
                        <div class="yt-search-title yt-search-artist-album" onclick="yt_get_album('${browse_id}')" title="${title}">${title}</div>
                        <div class="yt-search-bottom">
                            <div class="yt-search-type">${type}</div>
                            <span class="yt-search-bottom-separator"> • </span>
                            <div class="yt-search-year">${year}</div>
                        </div>
                    </div>
                    <div class="yt-search-more" onclick="yt_get_album_items(this, '${playlist_id}', '${browse_id}')">${icons.chevron_right}</div>
                </div>
                <div class="yt-search-album-items"></div>
            </div>`
            
        }

        yt_search_results_field.querySelector(".yt-search-artist-singles").innerHTML = yt_artist_singles;
    }
    
    old_results_field.insertAdjacentElement("afterend", yt_search_results_field);



}

async function yt_get_album(browse_id) {
    console.log(browse_id);

    var album = await yt_get_album_browse_id_req(browse_id, true)

    if (!album) {
        alert("Unexpected error. Please try again. If that doesn't help, try restarting SomeDL.");
        return;
    }


    var old_results_field = document.getElementById("yt-search-results-field")
    
    var history_id = old_results_field.className.match(/yt-search-results-field-history-(\d+)/);
    console.log(history_id);

    if (history_id) {
        var new_history_number = Number(history_id[1]) + 1
        var old_history_number = Number(history_id[1])
    } else {
        console.log("----- NO HIST ID!!!!!!");
        var new_history_number = 1
        var old_history_number = 0
    }

    old_results_field.removeAttribute('id');

    var yt_search_results_field = document.createElement("div");
    yt_search_results_field.id = "yt-search-results-field"
    yt_search_results_field.classList.add("yt-search-results-field")
    yt_search_results_field.classList.add("yt-search-results-field-history-" + new_history_number)


    console.log(album);

    album_art_url   = album.album_data.thumbnails[1]?.url;
    title           = album.album_data.title ?? "Album has no title";
    type            = album.album_data.type;
    year            = album.album_data.year;
    duration        = album.album_data.duration;
    track_count      = album.album_data.trackCount;
    playlist_id     = album.album_data.audioPlaylistId;

    artists_names_arr = []
    for (let i = 0; i < album.album_data.artists.length; i++) {
        artist = album.album_data.artists[i];
        artists_names_arr.push(`<span onclick="yt_get_artist_content('${artist.id}')">${artist.name}</span>`)
    }
    artists_names = artists_names_arr.join(", ")


    album_string = `
        <div class="yt-search-item">
            <button class="yt-search-artist-header-back-btn ui-button" onclick="yt_search_return_btn('yt-search-results-field-history-${old_history_number}')">${icons.chevron_left}</button>
            <div class="yt-search-coverart large">
                <img src="${album_art_url}" alt="Coverart">
                <button class="yt-search-download-btn"  onclick="yt_search_download('https://music.youtube.com/browse/${browse_id}', this)">${icons.download(true)}</button>
            </div>
            <div class="yt-search-text">
                <div class="yt-search-title large" title="${title}">${title}</div>
                <div class="yt-search-bottom">
                    <div class="yt-search-type">${type}</div>
                    <span class="yt-search-bottom-separator"> • </span>
                    <div class="yt-search-artist">${artists_names}</div>
                    <span class="yt-search-bottom-separator"> • </span>
                    <div class="yt-search-year">${year}</div>
                </div>
                <div class="yt-search-bottom">
                    <div class="yt-search-count">${track_count} songs</div>
                    <span class="yt-search-bottom-separator"> • </span>
                    <div class="yt-search-duration">${duration}</div>
                </div>
            </div>
        </div>
        <div class="yt-search-album-items"></div>
`


    yt_search_results_field.innerHTML = album_string;


    // === Add items ===
    album_results_string = "";

    for (let i = 0; i < album.result.tracks.length; i++) {
        const element = album.result.tracks[i];

        title           = element.title ?? "Song has no title";
        duration        = element.duration;
        video_id        = element.videoId;

        artists_names_arr = []
        for (let i = 0; i < element.artists.length; i++) {
            artist = element.artists[i];
            artists_names_arr.push(`<span onclick="yt_get_artist_content('${artist.id}')">${artist.name}</span>`)
        }
        artists_names = artists_names_arr.join(", ")

        album_results_string += `
            <div class="yt-search-item">
                <div class="yt-search-coverart">
                    <div class="yt-search-tracknumber">${i + 1}</div>
                    <button class="yt-search-download-btn" onclick="yt_search_download('https://music.youtube.com/watch?v=${video_id}', this)">${icons.download()}</button>
                </div>
                <div class="yt-search-text">
                    <div class="yt-search-title" title="${title}">${title}</div>
                    <div class="yt-search-bottom">
                        <div class="yt-search-artist">${artists_names}</div>
                        <span class="yt-search-bottom-separator"> • </span>
                        <div class="yt-search-duration">${duration}</div>
                    </div>
                </div>
            </div>`

        
    }

    yt_search_results_field.querySelector(".yt-search-album-items").innerHTML = album_results_string;



    old_results_field.insertAdjacentElement("afterend", yt_search_results_field);

}

async function yt_get_album_items(target, playlist_id, browse_id) {
    console.log(playlist_id)
    console.log(target)


    if (target.classList.contains("dd_open")) {
        // --- Is open -> close
        target.parentElement.parentElement.querySelector(".yt-search-album-items").style.display = "none";
        target.classList.remove("dd_open");
        target.classList.add("dd_closed");
        target.innerHTML = icons.chevron_right;
        return
    } else if (target.classList.contains("dd_closed")) {
        // --- Has already been opened -> reopen, do not fetch new data
        target.parentElement.parentElement.querySelector(".yt-search-album-items").style.display = "block";
        target.classList.add("dd_open");
        target.classList.remove("dd_closed");
        target.innerHTML = icons.chevron_down;
        return
    }

    // --- Look up data if not already present

    // target.classList.add("dd_open");
    // target.innerHTML = "O";

    // console.log(target.parentElement)
    // console.log(target.parentElement.parentElement)

    if (playlist_id != "undefined") {
        console.log("searching by playlist_id");
        console.log(playlist_id);
        
        data = await yt_get_album_req(playlist_id)
    } else {
        console.log("searching by browse_id");

        data = await yt_get_album_browse_id_req(browse_id)
    }
    
    
    console.log(data);
    if (!data) {
        alert("Unexpected error. Please try again. If that doesn't help, try restarting SomeDL.");
        return;
    }


    search_results_string = "";

    for (let i = 0; i < data.result.tracks.length; i++) {
        const element = data.result.tracks[i];

        title           = element.title ?? "Song has no title";
        // artists_names   = (element.artists || []).map(a => a.name).join(", ");
        duration        = element.duration;
        video_id        = element.videoId;
        // views           = element.views;

        artists_names_arr = []
        for (let i = 0; i < element.artists.length; i++) {
            artist = element.artists[i];
            artists_names_arr.push(`<span onclick="yt_get_artist_content('${artist.id}')">${artist.name}</span>`)
        }
        artists_names = artists_names_arr.join(", ")

        search_results_string += `
            <div class="yt-search-item">
                <div class="yt-search-coverart">
                    <div class="yt-search-tracknumber">${i + 1}</div>
                    <button class="yt-search-download-btn" onclick="yt_search_download('https://music.youtube.com/watch?v=${video_id}', this)">${icons.download()}</button>
                </div>
                <div class="yt-search-text">
                    <div class="yt-search-title" title="${title}">${title}</div>
                    <div class="yt-search-bottom">
                        <div class="yt-search-artist">${artists_names}</div>
                        <span class="yt-search-bottom-separator"> • </span>
                        <div class="yt-search-duration">${duration}</div>
                    </div>
                </div>
            </div>`
    }   

    target.parentElement.parentElement.querySelector(".yt-search-album-items").innerHTML = search_results_string
    target.classList.add("dd_open");
    target.innerHTML = icons.chevron_down;
}


function toggle_more_btn(target) {
    console.log(target);
    
    var btnText = target
    var dots = target.parentElement.querySelector(".toggle_more_dots");
    var moreText = target.parentElement.querySelector(".toggle_more");
    

    if (dots.style.display === "none") {
        dots.style.display = "inline";
        btnText.innerHTML = "MORE"; 
        moreText.style.display = "none";
    } else {
        dots.style.display = "none";
        btnText.innerHTML = "LESS"; 
        moreText.style.display = "inline";
    }
}

function yt_search_return_btn(return_to) {
    console.log(return_to);
    returned_item = document.querySelector("." + return_to);
    current_item = document.getElementById("yt-search-results-field");

    returned_item.id = "yt-search-results-field";
    current_item.remove();
}


function prompt_yt_download_artist(url, name) {

    alert_box(`Downloading discography of ${name}`, `
        <p>What do you want to include? Albums are always downloaded.</p>
        <p><i>The initialization of the download may take a couple of seconds</i></p>

        <input type="checkbox" name="yt-download-artist-selector" value="singles"> Include singles<br>
        <input type="checkbox" name="yt-download-artist-selector" value="other"> Include albums & singles where ${name} is not the main artist.<br>
        <br>
        <div class="popup-button-box">
            <button class="ui-button ui-button-small popup-exit"" onclick="yt_download_artist('${url}')">OK</button>
            <button class="ui-button ui-button-small popup-exit">Cancel</button>
        </div>  
    `);
}

function yt_download_artist(url) {

    var inp_fields = document.querySelectorAll('input[name="yt-download-artist-selector"]');
    const artist_presets = Object.fromEntries(
        Array.from(inp_fields).map(el => [el.value, el.checked])
    );
    console.log(artist_presets);

    yt_search_download(url, false, artist_presets);

}