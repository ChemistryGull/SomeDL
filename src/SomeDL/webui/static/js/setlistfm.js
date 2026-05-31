console.log("Helloooo");

var setlist_song_list = [];
var setlist_venue_list = []
var setlist_data = [];
var setlist_artist = "";
var setlist_artist_mbid = "";
var setlist_page_counter = 0;

async function setlistfm_artist_search() {
    document.getElementById("setlist_loading").style.display = "block";
    document.querySelector(".setlist_table_wrapper").style.display = "none";
    document.getElementById("setlist_error").style.display = "none";


    search_query = document.getElementById("setlistfm-artist-inp-field").value;
    artist_list = await setlist_artist_req(search_query);

    if (!artist_list.artist) {
        console.error(setlistfm_res);

        document.getElementById("setlist_error").innerHTML = `Error ${artist_list.code}: ${artist_list.message} (${artist_list.status})`
        document.getElementById("setlist_loading").style.display = "none";
        document.getElementById("setlist_error").style.display = "block";
        return
    }

    console.log(artist_list);
    artist_table = ""
    for (let i = 0; i < artist_list.artist.length; i++) {
        const element = artist_list.artist[i];

        artist_table += `
        <tr>
            <td onclick="setlist_init_load('${element.name}', '${element.mbid}')">${element.name}</td>
            <td>${element.disambiguation}</td>
            <td><a href="${element.url}">${element.mbid}</a></td>
        </tr>`
        
    }
    
    document.getElementById("setlist_loading").style.display = "none";
    document.querySelector(".setlist-artist-table").style.display = "block";
    document.getElementById("setlist_artist_table_body").innerHTML = artist_table;
    
}

function setlistfm_load_more() {
    setlist_load(setlist_artist, setlist_artist_mbid);
}

async function setlist_init_load(name, mbid) {
    setlist_song_list = [];
    setlist_venue_list = []
    setlist_data = [];  
    setlist_artist = name;
    setlist_artist_mbid = mbid;
    setlist_page_counter = 0;
    await setlist_load();
}

async function setlist_load() {
    document.getElementById("setlist_loading").style.display = "block";
    document.querySelector(".setlist-artist-table").style.display = "none";
    document.getElementById("setlist_loading").style.display = "block";
    document.getElementById("setlist_error").style.display = "none";

    // var setlistfm_res = test_setlist_data;
    setlist_page_counter++;
    var setlistfm_res = await setlist_get_req(setlist_artist_mbid, setlist_page_counter);
    console.log(setlistfm_res);
    if (!setlistfm_res.setlist) {
        console.error(setlistfm_res);
        
        document.getElementById("setlist_error").innerHTML = `Error ${setlistfm_res.code}: "${setlist_artist}" ${setlistfm_res.message} (${setlistfm_res.status})`
        document.getElementById("setlist_loading").style.display = "none";
        document.getElementById("setlist_error").style.display = "block";

        if (setlistfm_res.message.includes("page does not exist")) {
            document.getElementById("setlist_error").innerHTML = `Last entry reached, no more entries.`
        }

        return
    }
    

    for (let idx_venue = 0; idx_venue < setlistfm_res.setlist.length; idx_venue++) {
        const venue = setlistfm_res.setlist[idx_venue];
        
        var venue_data = {
            id: venue.id,
            name: venue.venue.name,
            date: venue.eventDate,
            url: venue.url,
            tour: venue.tour?.name || "(no tour)",
            country: venue.venue.city.country.name,
            country_code: venue.venue.city.country.code,
            city: venue.venue.city.name,
            selected: true
        }

        setlist_venue_list.push(venue_data)

        var song_list = Array(setlist_song_list.length).fill(null);

        for (let idx_set = 0; idx_set < venue.sets.set.length; idx_set++) {
            const set = venue.sets.set[idx_set];

            for (let idx_song = 0; idx_song < set.song.length; idx_song++) {
                const song = set.song[idx_song];

                if (song.name.trim() == "") {
                    continue;
                }
                
                var song_data = {
                    name: song.name,
                    selected: true,
                    cover: song.cover,
                    tape: song.tape,
                    with: song.with,
                    info: song.info?.replaceAll(`\"`, '"')?.replaceAll(`'`, '"')
                }
                
                index = setlist_song_list.findIndex(item => item && item.name.toLowerCase() == song.name.toLowerCase());
                
                if (index < 0) {
                    // --- Add new entry at the end
                    setlist_song_list.push(song_data)
                    song_list.push(song_data)

                    // --- Add null for each new song that has not been in the first songs
                    for (let i = 0; i < setlist_data.length; i++) {
                        setlist_data[i].push(null);
                    }

                } else {
                    // --- Add new entry at the current position of this song
                    song_list[index] = song_data
                }
            }
        }
        setlist_data.push(song_list)

    }


    setlist_build_table()
    document.querySelector(".setlist_table_wrapper").style.display = "block";
    document.getElementById("setlist_loading").style.display = "none";
}

function setlist_build_table() {

    // === Build header ===
    var head_html = `<tr><th id="setlist-topright-head" style="vertical-align: middle;"><h1 style="margin: 0;">${setlist_artist}</h1></th>`;
    for (let i = 0; i < setlist_venue_list.length; i++) {
        const venue = setlist_venue_list[i];
        head_html += `
        <th class="setlist-venue${venue.selected ? "" : " unselected"}" title="${venue.country}\n${venue.name}">
            <div>
                <div>${venue.date}</div>
                <hr>
                <div>${venue.city}</div>
                <div>${venue.country_code}</div>
            </div>
        </th>`
    }
    head_html += "</tr>"


    // === Build tour info ===
    head_html += `<tr><th style="font-size: 12px; z-index: 3"></th>`;
    var tour_entry_nr = 0;
    for (let i = 0; i <= setlist_venue_list.length; i++) {

        if (i == 0) {
            tour_entry_nr++;
        } else if (i != setlist_venue_list.length && setlist_venue_list[i - 1].tour.toLowerCase() == setlist_venue_list[i].tour.toLowerCase()) {
            tour_entry_nr++;
        } else {
            head_html += `<th colspan="${tour_entry_nr}" title="${setlist_venue_list[i - 1].tour}" class="setlist-tour-cell"><div>${setlist_venue_list[i - 1].tour}</div></th>`;
            tour_entry_nr = 1;
        }
    }
    head_html += "</tr>"

    
    // === Build body ===
    body_html = ""

    for (let i = 0; i < setlist_song_list.length; i++) {
        const song = setlist_song_list[i];

        var song_html = `<tr class="setlist-row${song.selected ? "" : " unselected"}">
        <td>
            <div class="song-name-column" title="${song.name}">
                <div>
                    ${song.name}
                </div>
                <div>
                    <span class="setlist_songs_nr">6</span>/<span class="setlist_songs_max">20</span>
                </div>      
            </div>
        </td>`;

        for (let j = 0; j < setlist_venue_list.length; j++) {
            const data = setlist_data[j][i]

            if (data) {
                // --- Add info to title if song is cover, played of tape. 
                var title_info = "";
                var is_special = false;
                var has_info = false;
                if (data.cover) {
                    title_info = title_info.concat(`\nCover of ${data.cover.name}`);
                    is_special = true;
                    has_info = true;
                }
                if (data.tape) {
                    title_info = title_info.concat(`\nSong played of tape`);
                    is_special = true;
                    has_info = true;
                }   

                if (data.with) {
                    title_info = title_info.concat(`\nPlayed with ${data.with.name?.replaceAll(`\"`, '"')?.replaceAll(`'`, '"')}`);
                    has_info = true;
                }

                if (data.info) {
                    title_info = title_info.concat(`\nInfo: ${data.info}`);
                    has_info = true;
                }

                song_html += `<td class="${setlist_venue_list[j].selected ? "" : "td-unselected"} ${is_special ? 'setlist-is-special' : ''}" title='${title_info.trim()}'><div class="setlist-body-item" ${has_info ? 'style="text-decoration: underline;"' : ''}>${song.name}</div></td>`;
            } else {
                song_html += `<td class="${setlist_venue_list[j].selected ? "" : "td-unselected"}">-</td>`;
            }
        }
        song_html += "</tr>";
        body_html += song_html
    }

    document.getElementById("setlist_thead").innerHTML = head_html;
    document.getElementById("setlist_tbody").innerHTML = body_html;


    setlist_process_selected_venues()


    // === column head click event listeners ===
    document.querySelectorAll("th.setlist-venue").forEach((el, index) => {
        el.addEventListener("click", () => {
            do_select = el.classList.contains("unselected"); // --- true if the venue is selected again
            if (do_select) {
                el.classList.remove("unselected")
                setlist_venue_list[index].selected = true;
            } else {
                el.classList.add("unselected")
                setlist_venue_list[index].selected = false;
            }        

            // --- Unselect/select songs in a column of the clicked venue.
            for (let i = 0; i < setlist_song_list.length; i++) {
                document.getElementById("setlist_tbody").rows[i].cells[index + 1].classList.toggle("td-unselected")
            }

            setlist_process_selected_venues()

        });
    });

    // === rows click event listeners ===
    document.querySelectorAll("tr.setlist-row").forEach((el, index) => {
        el.addEventListener("click", () => {
            if (el.classList.contains("unselected")) {
                el.classList.remove("unselected")
                setlist_song_list[index].selected = true;
            } else {
                el.classList.add("unselected")
                setlist_song_list[index].selected = false;
            }            
        });
    });

    
    setTimeout(() => {
        var first_row_width = document.getElementById("setlist-topright-head").offsetWidth + 10;
        document.querySelectorAll(".setlist_table th.setlist-tour-cell>div").forEach(el => {
            el.style.left = first_row_width + "px";
        });
    }, 0);
}

function setlist_process_selected_venues() {
    // === Check for songs to unselect because there are no more venues with that song selected ===
    var nr_selected = 0;
    var nr_venues = 0;

    for (let i = 0; i < setlist_song_list.length; i++) {
        for (let j = 0; j < setlist_venue_list.length; j++) {
            if (setlist_data[j][i] && setlist_venue_list[j].selected) {
                nr_selected++;
            }
            if (setlist_venue_list[j].selected) {
                nr_venues++;
            }
        }

        if (nr_selected > 0) {
            setlist_song_list[i].selected_venue = true;
            document.querySelectorAll('tr.setlist-row')[i].classList.remove("venue-unselected");
        } else {
            setlist_song_list[i].selected_venue = false;
            document.querySelectorAll('tr.setlist-row')[i].classList.add("venue-unselected")
        }
        document.querySelectorAll('tr.setlist-row')[i].querySelector(".setlist_songs_nr").innerHTML = nr_selected;
        document.querySelectorAll('tr.setlist-row')[i].querySelector(".setlist_songs_max").innerHTML = nr_venues;

        nr_selected = 0;
        nr_venues = 0;
        
    }
}

function setlistfm_download() {

    var download_list = [];
    for (let i = 0; i < setlist_song_list.length; i++) {
        const song = setlist_song_list[i];
        if (song.selected && song.selected_venue) {
            download_list.push(`${setlist_artist} - ${song.name}`);
        }
    }

    console.log(download_list);
    add_list(download_list)
}



// === drag and move table ===
setlist_scroll_area = document.getElementById("setlist_scroll_area")
var isDragging = false;
var startX, startY;
var scrollLeft, scrollTop;
const DRAG_THRESHOLD = 6; // --- pixels threshold till it will scroll instad of click

setlist_scroll_area.addEventListener('mousedown', e => {
    startX     = e.pageX;
    startY     = e.pageY;
    scrollLeft = setlist_scroll_area.scrollLeft;
    scrollTop  = setlist_scroll_area.scrollTop;
    isDragging = false;
});

window.addEventListener('mousemove', e => {
    if (!startX) return;
    const dist = Math.hypot(e.pageX - startX, e.pageY - startY);

    if (dist > DRAG_THRESHOLD) {
        isDragging = true
    }

    if (isDragging) {
        setlist_scroll_area.scrollLeft = scrollLeft - (e.pageX - startX);
        setlist_scroll_area.scrollTop  = scrollTop  - (e.pageY - startY);
    }
});


window.addEventListener('mouseup', () => { startX = 0; });

setlist_scroll_area.addEventListener('click', e => {
  if (isDragging) e.stopPropagation();
}, true);

