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
                <td>${el.mb_genres}</td>
                <td>${el.track_pos}/${el.track_count}</td>
                <td>${lyrics}</td>
                <td>${el.video_type.replace("MUSIC_VIDEO_TYPE_", "")}</td>
                <td><a target='_blank' href='https://music.youtube.com/watch?v=${el.song_id}'>${el.song_id}</a></td>
                <td>${Math.round(el.download_time * 10) / 10} seconds</td>
                <td>${el.filetype}</td>
            </tr>
        `
    }
    document.querySelector(".hist-tab-success tbody").innerHTML = new_table_content;
    document.querySelector(".hist-nr-success").innerHTML = data.metadata_success_list.length;


    // === Successful downloads ===
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


var test_history_data = {
    "already_downloaded_list": [
        {
            "album_id": "MPREb_O8hSbmgZVQE",
            "album_name": "Upside Down",
            "artist_all_names": [
                "Ad Infinitum"
            ],
            "artist_id": "UCSdu5ODAQF8g0yxYrYT9SAg",
            "artist_name": "Ad Infinitum",
            "duration": 196,
            "label": {
                "id": "17771583438755558000001",
                "text": "1/0 Ad Infinitum - Upside Down"
            },
            "somedl_id": "17771583438755558000001",
            "song_id": "xv0LLl3C-S0",
            "song_title": "Upside Down",
            "song_title_clean": "Upside Down",
            "text_query": "ad infinitum upside down",
            "video_type": "MUSIC_VIDEO_TYPE_ATV",
            "video_type_original": "Search query",
            "yt_url": "https://music.youtube.com/watch?v=xv0LLl3C-S0"
        }
    ],
    "failed_list": [],
    "metadata_success_list": [
        {
            "album_art": [
                {
                    "height": 60,
                    "url": "https://yt3.googleusercontent.com/TiGpV3mcWzcEvmKqlpejAQM_vr81V3jp8-uUL1b8pOGITZPM6iqtjLdR5r1ONvqfNThd4O9sdl5eAOL_CA=w60-h60-l90-rj",
                    "width": 60
                },
                {
                    "height": 120,
                    "url": "https://yt3.googleusercontent.com/TiGpV3mcWzcEvmKqlpejAQM_vr81V3jp8-uUL1b8pOGITZPM6iqtjLdR5r1ONvqfNThd4O9sdl5eAOL_CA=w120-h120-l90-rj",
                    "width": 120
                },
                {
                    "height": 226,
                    "url": "https://yt3.googleusercontent.com/TiGpV3mcWzcEvmKqlpejAQM_vr81V3jp8-uUL1b8pOGITZPM6iqtjLdR5r1ONvqfNThd4O9sdl5eAOL_CA=w226-h226-l90-rj",
                    "width": 226
                },
                {
                    "height": 544,
                    "url": "https://yt3.googleusercontent.com/TiGpV3mcWzcEvmKqlpejAQM_vr81V3jp8-uUL1b8pOGITZPM6iqtjLdR5r1ONvqfNThd4O9sdl5eAOL_CA=w544-h544-l90-rj",
                    "width": 544
                }
            ],
            "album_artist": "Ad Infinitum",
            "album_id": "MPREb_xAdXmUvqIuJ",
            "album_name": "Abyss",
            "artist_all_names": [
                "Ad Infinitum"
            ],
            "artist_id": "UCSdu5ODAQF8g0yxYrYT9SAg",
            "artist_name": "Ad Infinitum",
            "date": "2024",
            "deezer_album_id": 609361052,
            "deezer_album_label": "Napalm Records Handels GmbH",
            "deezer_album_name": "Abyss",
            "deezer_artist_name": "Ad Infinitum",
            "deezer_genres": [
                "Heavy Metal"
            ],
            "deezer_isrc": "ATN262430201",
            "download_time": 5.578117847442627,
            "duration": 269,
            "filetype": "mp3",
            "label": {
                "id": "17771583536421864000001",
                "text": "2/0 Ad Infinitum - Outer Space"
            },
            "mb_artist_mbid": "f9cfdf4e-a437-42f0-a9ff-f6a598fa803d",
            "mb_artist_name": "Ad Infinitum",
            "mb_genres": "symphonic metal",
            "metadata_time": 2.035766363143921,
            "somedl_id": "17771583536421864000001",
            "song_id": "DjdFbFP0j9Q",
            "song_title": "Outer Space",
            "song_title_clean": "Outer Space",
            "text_query": "ad infinitum outer space",
            "total_time": "7.6 seconds",
            "track_count": 10,
            "track_pos": 3,
            "track_pos_counted": 3,
            "type": "Album",
            "video_type": "MUSIC_VIDEO_TYPE_ATV",
            "video_type_original": "Search query",
            "yt_url": "https://music.youtube.com/watch?v=DjdFbFP0j9Q"
        },
        {
            "album_art": [
                {
                    "height": 60,
                    "url": "https://yt3.googleusercontent.com/MiGAO5GM-QtAY3GDOlYXu3NdIX94bfOpY7cAkOgHxbXN3Ukz-IJl1VQsXfmEvCoLQrCo6LlGE1C8AuPB=w60-h60-l90-rj",
                    "width": 60
                },
                {
                    "height": 120,
                    "url": "https://yt3.googleusercontent.com/MiGAO5GM-QtAY3GDOlYXu3NdIX94bfOpY7cAkOgHxbXN3Ukz-IJl1VQsXfmEvCoLQrCo6LlGE1C8AuPB=w120-h120-l90-rj",
                    "width": 120
                },
                {
                    "height": 226,
                    "url": "https://yt3.googleusercontent.com/MiGAO5GM-QtAY3GDOlYXu3NdIX94bfOpY7cAkOgHxbXN3Ukz-IJl1VQsXfmEvCoLQrCo6LlGE1C8AuPB=w226-h226-l90-rj",
                    "width": 226
                },
                {
                    "height": 544,
                    "url": "https://yt3.googleusercontent.com/MiGAO5GM-QtAY3GDOlYXu3NdIX94bfOpY7cAkOgHxbXN3Ukz-IJl1VQsXfmEvCoLQrCo6LlGE1C8AuPB=w544-h544-l90-rj",
                    "width": 544
                }
            ],
            "album_artist": "Musica Ad Infinitum",
            "album_id": "MPREb_PekGFxzGdcR",
            "album_name": "夜ジャズbgm",
            "artist_all_names": [
                "Musica Ad Infinitum"
            ],
            "artist_id": "UCQ5RIPz-CFqcXRm52pmFbIA",
            "artist_name": "Musica Ad Infinitum",
            "date": "2022",
            "deezer_album_id": "No deezer album id found",
            "deezer_album_label": null,
            "deezer_album_name": "No deezer album name found",
            "deezer_artist_name": "No deezer artist name found",
            "deezer_genres": [],
            "deezer_isrc": "",
            "download_time": 4.538473844528198,
            "duration": 162,
            "filetype": "mp3",
            "label": {
                "id": "17771583636336972000001",
                "text": "3/0 Musica Ad Infinitum - Dreamy Dance"
            },
            "metadata_time": 2.4217705726623535,
            "somedl_id": "17771583636336972000001",
            "song_id": "kbXig3Yvzt0",
            "song_title": "Dreamy Dance",
            "song_title_clean": "Dreamy Dance",
            "text_query": "ad infinitum dance",
            "total_time": "7.0 seconds",
            "track_count": 30,
            "track_pos": 23,
            "track_pos_counted": 23,
            "type": "Album",
            "video_type": "MUSIC_VIDEO_TYPE_ATV",
            "video_type_original": "Search query",
            "yt_url": "https://music.youtube.com/watch?v=kbXig3Yvzt0"
        }
    ]
}