async function refresh_history() {
    const data = await refresh_history_req()
    // const data = test_history_data;
    console.log(data)


    // === Successful downloads ===
    var new_table_content = "";

    for (let i = 0; i < data.metadata_success_list.length; i++) {
        const el = data.metadata_success_list[i];

        if (el.instrumental) {
            var lyrics = "Instrumental"
        } else if (el.lyrics_synced) {
            var lyrics = "Synced"
        } else if (el.lyrics_plain) {
            var lyrics = "Plain"
        } else {
            var lyrics = "None"
        }
        
        const path = el.path;
        const dir = path.substring(0, path.lastIndexOf('/'));

        new_table_content += `
            <tr>
                <td class="dl-hist-album-art">
                    <a target='_blank' href='${el.album_art[el.album_art.length - 1].url}'>
                        <img src="${el.album_art[0].url}" alt="">
                    </a>
                </td>
                <td>${el.artist_name}</td>
                <td>${el.song_title}</td>
                <td>${el.album_name}</td>
                <td>${el.date}</td>
                <td>${el.mb_genres ?? ""}</td>
                <td>${el.track_pos}/${el.track_count}</td>
                <td>${lyrics}</td>
                <td>${el.video_type.replace("MUSIC_VIDEO_TYPE_", "")}</td>
                <td><a target='_blank' href='https://music.youtube.com/watch?v=${el.song_id}'>${el.song_id}</a></td>
                <td>${Math.round(el.download_time * 10) / 10} seconds</td>
                <td>${el.filetype}</td>
                <td class="dl-hist-btn">
                    <div class="dl-hist-btn-wrap">
                        <div class="dl-item-play-song" title="Open file in music player" onclick="req_open_file('${path}')">${icons.play}</div>
                        <div class="dl-item-open-folder" title="Open containing folder" onclick="req_open_file('${dir}')">${icons.open_folder}</div>
                    </div>
                </td>
            </tr>
        `
    }
    document.querySelector(".hist-tab-success tbody").innerHTML = new_table_content;
    document.querySelector(".hist-nr-success").innerHTML = data.metadata_success_list.length;


    // === Already downloaded downloads ===
    var new_table_content = "";

    for (let i = 0; i < data.already_downloaded_list.length; i++) {
        const el = data.already_downloaded_list[i];
       
        new_table_content += `
            <tr>
                <td>${el.text_query || "-"}</td>
                <td>${el.artist_name || "-"}</td>
                <td>${el.song_title || "-"}</td>
                <td>${el.video_type?.replace("MUSIC_VIDEO_TYPE_", "") || "-"}</td>
                <td><a target='_blank' href='https://music.youtube.com/watch?v=${el.song_id}'>${el.song_id  || "-"}</a></td>
            </tr>
        `
    }
    document.querySelector(".hist-tab-already tbody").innerHTML = new_table_content;
    document.querySelector(".hist-nr-already").innerHTML = data.already_downloaded_list.length;


    // === Failed downloads ===
    var new_table_content = "";

    for (let i = 0; i < data.failed_list.length; i++) {
        const el = data.failed_list[i];
       
        new_table_content += `
            <tr>
                <td>${el.text_query || "-"}</td>
                <td>${el.artist_name || "-"}</td>
                <td>${el.song_title || "-"}</td>
                <td>${el.video_type?.replace("MUSIC_VIDEO_TYPE_", "") || "-"}</td>
                <td><a target='_blank' href='https://music.youtube.com/watch?v=${el.song_id}'>${el.song_id  || "-"}</a></td>
                <td>${el.error || "-"}</td>
            </tr>
        `
    }
    document.querySelector(".hist-tab-failed tbody").innerHTML = new_table_content;
    document.querySelector(".hist-nr-failed").innerHTML = data.failed_list.length;

    document.querySelectorAll(".hist-nr-all").forEach((node) => {
        node.innerHTML = data.metadata_success_list.length + data.already_downloaded_list.length + data.failed_list.length;
    })

}


document.querySelectorAll("input[name='hist-tab-switch']").forEach(el => {
    el.addEventListener("change", () => {
        document.querySelectorAll(".hist-tab").forEach((node) => {
            node.style.display = "none";
        })
        document.querySelector(".hist-tab-" + el.value).style.display = "block";
    })
});


async function download_report() {
    const html = await req_get_download_report()
    if (!html) {
        return;
    }

    const d = new Date();
    const formatted_date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}-${String(d.getMinutes()).padStart(2, "0")}-${String(d.getSeconds()).padStart(2, "0")}`;

    const blob = new Blob([html], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `Download Report ${formatted_date}.html`;

    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

}

async function clear_history() {
    await req_clear_download_history();
    refresh_history();
}
