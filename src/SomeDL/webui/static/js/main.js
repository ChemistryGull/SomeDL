var active_page = "";
var dl_status_active = true;



// === Tasks for window.onload ===
window.onload = async function () {
    // --- Load WebUI
    await settings.webui_config_load()
    settings.init_webui_appearance(settings.webui_preset_themes);
    settings.init_webui_appearance(settings.webui_settings.custom_themes);
    settings.webui_update(settings.webui_settings.active_theme);
    
    // --- Load Settings
    await settings.load();
    settings.remember_current();

    // --- Get downloader state
    const downloader_state = await get_downloader_state();
    if (downloader_state.is_running) {
        document.querySelectorAll(".download-btn-pause").forEach(el => el.style.display = "flex");
        document.querySelectorAll(".download-btn-resume").forEach(el => el.style.display = "none");        
    } else {
        document.querySelectorAll(".download-btn-pause").forEach(el => el.style.display = "none");
        document.querySelectorAll(".download-btn-resume").forEach(el => el.style.display = "flex");   
    }

    // --- Refetch download queue
    refresh_queue_items();

    // --- Initialize status fetching loop
    // setInterval(dl_update_status, 500);
    dl_update_status_loop();

    // --- Load version
    const version = await get_version();
    if (version) {
        document.querySelector(".version").innerHTML = "v" + version.v;
    }

}



// === Initialize coloris without transparancy ===
Coloris({
  alpha: false
});


// === UI Navigation ===
function load_page(page) {
    active_page = page;
    console.log("Loading page: " + page)
    
    document.querySelectorAll('.page').forEach(el => {
        el.style.display = 'none';
        el.classList.remove('active-page');
    });
    document.getElementById("page-" + page).style.display = "block";


    document.querySelectorAll('.navbar-item').forEach(el => {
        el.classList.remove('active-page');
    });

    // document.getElementById("navbar-" + page).classList.add('active-page');
    document.querySelectorAll(".navbar-" + page).forEach((el) => {
        el.classList.add('active-page');
    })


    if (page == "download") {
        // --- Set dl_status_active to true to fetch updates for the download field. Will turn false after that if the queue is empty.
        dl_status_active = true;
    } else if (page == "download-history") {
        refresh_history();
    }

}

load_page("download")
// load_page("search")
// load_page("setlist")
// load_page("download-history")
// load_page("settings")


// === Help screen ===
function display_help() {
    alert_box('SomeDL WebUI Guide<button class="popup-close">✕</button>', `
        <div class="help-info-wrapper">
            Disclaimer: This WebUI is still very new, so there may be bugs and inconsistencies. Please report bugs and suggest changes on <a href="https://github.com/ChemistryGull/SomeDL" target="_blank">GitHub</a>.
            <h3>${icons.download()}Download</h3>
            <p>Paste a YouTube link, playlist, album URL or a search query directly into the input field to start downloading. You can download multiple songs at once by seperating them with commas.</p>
            <p>Below the input field you'll see status updates for your current downloads. Hover over any queued item and click the trash icon to remove it.</p>
            <p>The bottom-left corner shows an overview of your download queue and finished downloads. Below that there is a control bar with the following options:</p>
            <ul>
                <li><b>Shutdown:</b> Shut down the SomeDL server.</li>
                <li><b>Pause/Resume:</b> Use the pause button to pause downloading (anything already active will finish).</li>
                <li><b>Trash:</b> The trash icon clears the entire queue at once.</li>
                <li><b>Question mark:</b> Shows this message.</li>
            </ul>
            <p>Change the download format, output folder and more in the settings tab. (don't forget to apply!)</p>
            <p>If a download fails, try again. Often it works on the second try. If it still fails, there might be other problems, like the song being age restricted (<a target="_blank" href="https://somedl.readthedocs.io/en/latest/usage/howto.html#how-do-i-download-age-restricted-songs">How to circumvent this</a>). Also view the command-line output for additional information.</p>

            <h3>${icons.search}YouTube Search</h3>
            <p>Search for songs, albums, or artists just like you would on YouTube Music, Spotify etc. Click a cover image to add that item to your download queue. You can also click on the artists or albums for additional information.</p>

            <h3>${icons.setlist}Setlist</h3>
            <p>Search for a band or artist to display their concert setlists history. From there you can deselect any songs or venues you don't want and load more shows with the +20 button. When you're happy with your selection, press the download button in the top-left corner.</p>
            <p>Extra information in the table:</p>
            <ul>
                <li><u>Underlined</u> Underlined song titles contain extra info. Hover over them to see it.</li>
                <li><i>Italic</i> Covers and songs played from tape are italic. Hover over them for exact information.</li>
            </ul>
            <p>Setlist data is provided by <a href="https://setlist.fm" target="_blank">setlist.fm</a>. Their API is rate-limited, so please avoid making a large amount of searche requests in rapid succession.</p>

            <h3>${icons.history}Download History</h3>
            <p>Similar to the download report, the download history shows information of all downloaded songs. Resets when application is restarted.</p>
            
            <h3>${icons.settings}Settings</h3>
            <p>The settings menu lets you change SomeDL's configuration without interacting with the config file directly. Click the (?) next to any option for a description of what each setting does.</p>
            <ul>
                <li><b>Apply:</b> saves and applies the changes to your current session. This works for most settings, but be aware that some settings do require a full application restart to be applied properly.</li>
                <li><b>Reset:</b> undoes any unsaved changes</li>
                <li><b>Defaults:</b> restores all settings to their default values</li>
            </ul>
            <p>You can change the appearance of the SomeDL WebUI, pick another theme in at the bottom of the settings tab, or create a new theme.</p>
            <br>
            <hr>
            <h4>Contact</h4>
            <ul>
                <li>Need more info? Visit the <a href="https://github.com/ChemistryGull/SomeDL" target="_blank">GitHub page</a> and the <a href="https://somedl.readthedocs.io/en/latest/index.html" target="_blank">ReadTheDocs Page</a></li>
                <li>Need help? Ask <a href="https://github.com/ChemistryGull/SomeDL/discussions" target="_blank">here</a></li>
                <li>Tips or ideas? Tell me <a href="https://github.com/ChemistryGull/SomeDL/discussions/categories/ideas" target="_blank">here</a></li>
                <li>Found a bug? Tell me <a href="https://github.com/ChemistryGull/SomeDL/issues" target="_blank">here</a></li>
                <li>Like SomeDL? Leave a star on my <a href="https://github.com/ChemistryGull/SomeDL" target="_blank">GitHub repo</a>! :)</li>
            </ul>

            <h4>Credits</h4>
            <ul>
                <li>Setlist data by <a href="https://setlist.fm" target="_blank">setlist.fm</a></li>
                <li>Icons by <a href="https://tabler.io/icons" target="_blank">tabler.io</a></li>
                <li>Color picker by <a href="https://coloris.js.org/" target="_blank">Coloris</a></li>
                <li>Unofficial YouTube Music API: <a href="https://github.com/sigma67/ytmusicapi" target="_blank">ytmusicapi</a></li>
            </ul>

            <br>
            <i>This entire project is developed by a human. No part of this project is made with generative AI.</i>
        </div>
        `)
}


// === Show sidebar on mobile ===
function display_sidebar() {
    document.querySelector(".sidebar-download-tracker").classList.toggle("visible");
}


// === Loader function ===
var loader = {
    counter: 0,
    start () {
        this.counter++;
        setTimeout(() => {
            // --- Don't show loading spinner in the fist 100 ms
            if (this.counter > 0) {
                document.querySelector("#loading-spinner>svg").style.display = "block";
            }
        }, 100)
    },
    stop (message) {
        this.counter--;
        
        if (this.counter <= 0) {
            document.querySelector("#loading-spinner>svg").style.display = "none";
            this.counter = 0
        }

        if (message) {
            const el = document.createElement("span");
            el.classList.add("loading-message", "loading-message-error");
            el.textContent = message;
            document.getElementById("loading-spinner").prepend(el);
            setTimeout(() => {
                el.classList.add("loading-message-fade-out");

                // wait for fade transition to finish, then remove
                el.addEventListener("transitionend", () => {
                    el.remove();
                });
            }, 5000);
        }
    }
    
}

// === Flying download button ===

function flying_download_button(target) {

    var original_img = target.parentNode.querySelector("img");
    if (!original_img) {
        original_img = target.parentNode.querySelector(".yt-search-tracknumber");
    }

    if (window.matchMedia("(max-width: 768px)").matches) {
        // Go to download navbar button on mobile
        var sidebar_download_tracker = document.querySelector(".navbar-download.mobile")
    } else {
        var sidebar_download_tracker = document.querySelector(".sidebar-download-tracker")
    }

    var cloned_img = original_img.cloneNode(true);    
    const cloned_pos = original_img.getBoundingClientRect();
    const cloned_target_pos = sidebar_download_tracker.getBoundingClientRect();
    
    console.log(cloned_pos);
    

    document.body.appendChild(cloned_img);

    var distance = Math.sqrt((cloned_pos.left - cloned_target_pos.left)**2 + (cloned_pos.top - cloned_target_pos.top)**2)
    var SPEED = 800; // px/s
    var animation_time = Math.max(Math.round(10 * distance / SPEED) / 10, 0.4)
    var random_angle = Math.floor(Math.random() * 90) - 45;

    console.log(distance);
    console.log(animation_time);
    console.log(random_angle);
    console.log(Math.round(10 * distance / SPEED) / 10);
    

    // --- Original pos
    cloned_img.style.position = 'absolute';
    cloned_img.style.borderRadius = '0.5rem';
    cloned_img.style.height = cloned_pos.height + 'px';
    cloned_img.style.width = cloned_pos.width + 'px';
    cloned_img.style.opacity = '1';
    cloned_img.style.left = cloned_pos.left + 'px';
    cloned_img.style.top = cloned_pos.top + 'px';
    cloned_img.style.transform = 'rotate(0deg)';
    cloned_img.style.transition = `left ${animation_time}s linear, top ${animation_time}s ease-in, transform ${animation_time}s ease, height ${animation_time}s ease-in, width ${animation_time}s ease-in, opacity ${animation_time * 2}s linear`;
    // cloned_img.style.transition = `left ${animation_time}s linear, top ${animation_time}s linear`;


    cloned_img.offsetLeft; // --- trick: forche the browser to render the above changes so that the changes to the pos below will show the animation

    // --- Fly to new pos
    cloned_img.style.left = (cloned_target_pos.left + 20 + Math.random() * 140) + 'px';
    cloned_img.style.top = (cloned_target_pos.top + 5 + Math.random() * 47) + 'px';
    cloned_img.style.height = '40px';
    cloned_img.style.width = '40px';
    cloned_img.style.transform = `rotate(${random_angle}deg)`;
    cloned_img.style.opacity = '0';

    cloned_img.addEventListener('transitionend', (e) => {
        // if (e.propertyName === 'left') {
        //     sidebar_download_tracker.style.borderColor = 'lightgrey';
        //     setTimeout(() => sidebar_download_tracker.style.borderColor = '', 50);
        // } 
        if (e.propertyName === 'opacity') {
            cloned_img.remove();
        }
    });
  

    
}



// === drag and move table ===
const DRAG_THRESHOLD = 6;

var activeArea = null;
var startX = 0;
var startY = 0;
var scrollLeft = 0;
var scrollTop = 0;
var isDragging = false;

document.querySelectorAll('.scroll-area').forEach(area => {

    area.addEventListener('pointerdown', e => {
        activeArea = area;

        startX = e.pageX;
        startY = e.pageY;

        scrollLeft = area.scrollLeft;
        scrollTop  = area.scrollTop;

        isDragging = false;

    });

    area.addEventListener('click', e => {
        if (isDragging) e.stopPropagation();
    }, true);
});

window.addEventListener('pointermove', e => {
    if (!activeArea) return;

    const selection = window.getSelection();
    if (selection && selection.toString().length > 0) {
        return; // --- don't scroll when something is selected
    }

    const dx = e.pageX - startX;
    const dy = e.pageY - startY;
    const dist = Math.hypot(dx, dy);
    activeArea.style.userSelect = 'none';

    if (dist > DRAG_THRESHOLD) {
        isDragging = true;

        activeArea.scrollLeft = scrollLeft - dx;
        activeArea.scrollTop  = scrollTop  - dy;
    }
});

window.addEventListener('pointerup', () => {
    if (activeArea) {
        activeArea.style.userSelect = '';
    }
    activeArea = null;
});



// === Icons ===
var icons = {
    download(large = false) {
        var icon_class = large ? "icon-yt-dl-button-large" : "icon-yt-dl-button-small";
        return `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${icon_class} icon icon-tabler icons-tabler-outline icon-tabler-download"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2" /><path d="M7 11l5 5l5 -5" /><path d="M12 4l0 12" /></svg>`;
    },
    chevron_left: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-chevron-left"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M15 6l-6 6l6 6" /></svg>`,
    chevron_right: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-chevron-right"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M9 6l6 6l-6 6" /></svg>`,
    chevron_down: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-chevron-down"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M6 9l6 6l6 -6" /></svg>`,
    trash: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-trash"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M4 7l16 0" /><path d="M10 11l0 6" /><path d="M14 11l0 6" /><path d="M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2 -2l1 -12" /><path d="M9 7v-3a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v3" /></svg>`,
    edit: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-edit"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M7 7h-1a2 2 0 0 0 -2 2v9a2 2 0 0 0 2 2h9a2 2 0 0 0 2 -2v-1" /><path d="M20.385 6.585a2.1 2.1 0 0 0 -2.97 -2.97l-8.415 8.385v3h3l8.385 -8.415" /><path d="M16 5l3 3" /></svg>`,
    search: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-search"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M3 10a7 7 0 1 0 14 0a7 7 0 1 0 -14 0" /><path d="M21 21l-6 -6" /></svg>`,
    setlist: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-hand-love-you"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M11 11.5v-1a1.5 1.5 0 0 1 3 0v1.5" /><path d="M17 12v-6.5a1.5 1.5 0 0 1 3 0v10.5a6 6 0 0 1 -6 6h-2h.208a6 6 0 0 1 -5.012 -2.7a69.74 69.74 0 0 1 -.196 -.3c-.312 -.479 -1.407 -2.388 -3.286 -5.728a1.5 1.5 0 0 1 .536 -2.022a1.867 1.867 0 0 1 2.28 .28l1.47 1.47" /><path d="M14 10.5a1.5 1.5 0 0 1 3 0v1.5" /><path d="M8 13v-8.5a1.5 1.5 0 0 1 3 0v7.5" /></svg>`,
    history: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-history"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M12 8l0 4l2 2" /><path d="M3.05 11a9 9 0 1 1 .5 4m-.5 5v-5h5" /></svg>`,
    settings: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-settings"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M10.325 4.317c.426 -1.756 2.924 -1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543 -.94 3.31 .826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572c1.756 .426 1.756 2.924 0 3.35a1.724 1.724 0 0 0 -1.066 2.573c.94 1.543 -.826 3.31 -2.37 2.37a1.724 1.724 0 0 0 -2.572 1.065c-.426 1.756 -2.924 1.756 -3.35 0a1.724 1.724 0 0 0 -2.573 -1.066c-1.543 .94 -3.31 -.826 -2.37 -2.37a1.724 1.724 0 0 0 -1.065 -2.572c-1.756 -.426 -1.756 -2.924 0 -3.35a1.724 1.724 0 0 0 1.066 -2.573c-.94 -1.543 .826 -3.31 2.37 -2.37c1 .608 2.296 .07 2.572 -1.065" /><path d="M9 12a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" /></svg>`,
    loader: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-loader-4"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M12 21v-3m6.36 .36l-2.12 -2.12m4.76 -4.24h-3m.36 -6.36l-2.12 2.12m-4.24 -4.76v3m-6.36 -.36l2.12 2.12m-3.76 4.24h2m1 4.95l.71 -.71" /></svg>`,
    open_folder: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-folder-open"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M5 19l2.757 -7.351a1 1 0 0 1 .936 -.649h12.307a1 1 0 0 1 .986 1.164l-.996 5.211a2 2 0 0 1 -1.964 1.625h-14.026a2 2 0 0 1 -2 -2v-11a2 2 0 0 1 2 -2h4l3 3h7a2 2 0 0 1 2 2v2" /></svg>`,
    play: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-player-play"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M7 4v16l13 -8l-13 -8" /></svg>`,
    file_download: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-file-download"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M14 3v4a1 1 0 0 0 1 1h4" /><path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2" /><path d="M12 17v-6" /><path d="M9.5 14.5l2.5 2.5l2.5 -2.5" /></svg>`,
    external_link: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-external-link"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M12 6h-6a2 2 0 0 0 -2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-6" /><path d="M11 13l9 -9" /><path d="M15 4h5v5" /></svg>`,
    redownload: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-circle-open-arrow-down"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M15.998 3.934a9 9 0 1 1 -3.998 -.934v13" /><path d="M16 12l-4 4l-4 -4" /></svg>`,
    sort_alphabetically: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-sort-ascending-letters"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M15 10v-5c0 -1.38 .62 -2 2 -2s2 .62 2 2v5m0 -3h-4" /><path d="M19 21h-4l4 -7h-4" /><path d="M4 15l3 3l3 -3" /><path d="M7 6v12" /></svg>`
}