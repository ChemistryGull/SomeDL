import json
import time
from html import escape
from pathlib import Path

import SomeDL.utils.console as console
from SomeDL.utils.config import config
from SomeDL.utils.version import VERSION

def build_download_report(data, failed, already_downloaded = []):
    
    len_success = len(data)
    len_failed = len(failed)
    len_already_downloaded = len(already_downloaded)
    len_total = len_success + len_failed + len_already_downloaded
    
    title = "Playlist download report"

    head = f"""
        <h1>Download Report {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - SomeDL version {VERSION}</h1>
        <p><i>Don't want these download reports? Disable them with </i><code>somedl --disable-report</code></p>
        <p>Summary: Out of {len_total} songs, {len_success} were downloaded successfully, {len_failed} songs failed to download and {len_already_downloaded} songs were already present.</p>
        <button onclick='check_downloads()'>Scan for Possible Mismatches</button>
        <p id="check_results"></p>
        <button onclick="download_CSV()">Download as CSV</button>
        <select id="csv-table-select">
            <option value="table-success" selected>Successful Downloads</option>
            <option value="table-failed">Failed Downloads</option>
            <option value="table-already">Already Downloaded</option>
        </select>
    """

    # === Success ===

    relevant_keys = [
        ["No.", "!special"],
        ["Input Type", "!special"],
        ["Searched Song", "!special"],
        ["Artist", "artist_name"],
        ["Title", "song_title"],
        ["Album", "album_name"],
        ["Year", "date"],
        ["Genre", "mb_genres"],
        ["Track", "!special"],
        ["Lyrics", "!special"],
        ["Video Type", "!special"],
        ["URL", "!special"],
        ["Albumart", "!special"],
        ["Download time", "total_time"],
        ["Filetype", "filetype"],
        ["File", "!special"]
    ]

    table_success = ["<table id='table-success'>"]

    # Header
    table_success.append("<thead><tr>")
    for header in relevant_keys:
        table_success.append(f'<th>{escape(str(header[0]))}</th>')
    table_success.append("</tr></thead>")

    # Body
    table_success.append("<tbody>")
    for item in data:
        table_success.append("<tr>")
        for header in relevant_keys:
            if header[1] == "!special":
                # --- All items that require special formatting
                match header[0]:
                    case "No.":
                        if item.get("label"):
                            table_success.append(f'<td>{escape(item.get("label").get("text").split("/", 1)[0])}</td>')
                        else:
                            table_success.append(f"<td></td>")

                    case "Input Type":
                        match item.get("inp_type"):
                            case "Search query":
                                table_success.append(f"<td>Query</td>")
                                table_success.append(f"<td>{escape(item.get('text_query'))}</td>")
                            case "Playlist":
                                table_success.append(f"<td><a target='_blank' href=\"https://music.youtube.com/playlist?list={escape(item.get('playlist_id'))}\">Playlist</a></td>")
                                table_success.append(f"<td>{escape(item.get('artist_name_original'))} - {escape(item.get('song_title_original'))}</td>")
                            case "Song":
                                table_success.append(f"<td><a target='_blank' href=\"https://music.youtube.com/watch?v={escape(item.get('song_id'))}\">Song</a></td>")
                                table_success.append(f"<td>{escape(item.get('artist_name_original'))} - {escape(item.get('song_title_original'))}</td>")
                            case "Album":
                                table_success.append(f"<td><a target='_blank' href=\"https://music.youtube.com/browse/{escape(item.get('album_id'))}\">Album</a></td>")
                                table_success.append(f"<td>{escape(item.get('artist_name_original'))} - {escape(item.get('song_title_original'))}</td>")
                            case "Artist":
                                table_success.append(f"<td><a target='_blank' href=\"https://music.youtube.com/browse/{escape(item.get('artist_id'))}\">Artist</a></td>")
                                table_success.append(f"<td>{escape(item.get('artist_name_original'))} - {escape(item.get('song_title_original'))}</td>")

                            case "Fetch Albums":
                                table_success.append(f"<td>Fetch Albums</td>")
                                table_success.append(f"<td><i>{escape(item.get('fetch_album_origin'))}</i></td>")

                            case _:
                                table_success.append(f"<td></td>")
                                table_success.append(f"<td></td>")

                    case "Lyrics":
                        if item.get("instrumental"):
                            table_success.append(f"<td>Instrumental</td>")
                        elif item.get("lyrics_synced") and item.get("lyrics_plain") and config["metadata"]["lyrics_type"] == "both":
                            table_success.append(f"<td>Synced&Plain</td>")
                        elif item.get("lyrics_synced") and config["metadata"]["lyrics_type"] in ["both", "synced", "synced_if_available"]:
                            table_success.append(f"<td>Synced</td>")
                        elif item.get("lyrics_plain") and config["metadata"]["lyrics_type"] in ["both", "plain", "synced_if_available"]:
                            table_success.append(f"<td>Plain</td>")
                        else: 
                            table_success.append(f"<td>No</td>")
                    case "Albumart":
                        if not item.get("album_art"):
                            table_success.append(f"<td></td>")
                        elif not len(item.get("album_art", [{}])) == 0:
                            album_art_url = item.get("album_art", [{}])[-1].get("url")
                            table_success.append(f"<td><a target='_blank' href=\"{escape(album_art_url)}\">Yes</a></td>")
                        else:
                            table_success.append(f"<td>No</td>")
                    case "URL":
                        if not item.get("yt_url"):
                            table_success.append(f"<td></td>")
                        else:
                            yt_url = item.get("yt_url")
                            table_success.append(f"<td><a target='_blank' href=\"{escape(yt_url)}\">{escape(yt_url.replace('https://music.youtube.com/watch?v=', '').replace('https://www.youtube.com/watch?v=', ''))}</a></td>")
                    case "Track":
                        trackof = f'{item.get("track_pos")}/{item.get("track_count")}'
                        table_success.append(f"<td>{escape(trackof)}</td>")
                    case "Video Type":
                        table_success.append(f'<td>{escape((item.get("video_type_original", "") or "").replace("MUSIC_VIDEO_TYPE_", ""))}</td>')

                    case "File":
                        table_success.append(f"<td><a target='_blank' href=\"{escape(item.get('path', '') or '')}\">{escape(item.get('path', '~No data~') or '')}</a></td>")


            else:
                table_success.append(f'<td>{escape(str(item.get(header[1], "~No data~")))}</td>')
        table_success.append("</tr>")
    table_success.append("</tbody>")
    table_success.append("</table>")

    # === Failed ===


    table_failed = ["<table id='table-failed'>"]

    table_failed.append("<thead><tr>")
    table_failed.append("<th>No.</th>")
    table_failed.append("<th>Input Query</th>")
    table_failed.append("<th>Artist Name</th>")
    table_failed.append("<th>Song Name</th>")
    table_failed.append("<th>Video Type</th>")
    table_failed.append("<th>Youtube URL</th>")
    table_failed.append("<th>Error</th>")

    table_failed.append("</tr></thead>")

    table_failed.append("<tbody>")

    for item in failed:
        table_failed.append("<tr>")
        if item.get("label"):
            table_failed.append(f'<td>{escape(item.get("label").get("text").split("/", 1)[0])}</td>')
        else:
            table_failed.append(f'<td></td>')
        table_failed.append(f'<td>{escape(str(item.get("text_query", "-")))}</td>')
        table_failed.append(f'<td>{escape(str(item.get("artist_name", "-")))}</td>')
        table_failed.append(f'<td>{escape(str(item.get("song_title", "-")))}</td>')
        table_failed.append(f'<td>{escape((item.get("video_type_original", "") or "").replace("MUSIC_VIDEO_TYPE_", ""))}</td>')
        table_failed.append(f'<td>{escape(str(item.get("yt_url", "-")))}</td>')
        table_failed.append(f'<td>{escape(str(item.get("error", "-")))}</td>')
        table_failed.append("</tr>")
    table_failed.append("</tbody>")

    table_failed.append("</table>")
    


    # === Already downloaded ===


    table_already = ["<table id='table-already'>"]

    table_already.append("<thead><tr>")
    table_already.append("<th>No.</th>")
    table_already.append("<th>Input Query</th>")
    table_already.append("<th>Artist Name</th>")
    table_already.append("<th>Song Name</th>")
    table_already.append("<th>Video Type</th>")
    table_already.append("<th>Youtube URL</th>")
    table_already.append("<th>File</th>")

    table_already.append("</tr></thead>")

    table_already.append("<tbody>")

    for item in already_downloaded:
        table_already.append("<tr>")
        if item.get("label"):
            table_already.append(f'<td>{escape(item.get("label").get("text").split("/", 1)[0])}</td>')
        else:
            table_already.append(f'<td></td>')
        table_already.append(f'<td>{escape(str(item.get("text_query", "-")))}</td>')
        table_already.append(f'<td>{escape(str(item.get("artist_name", "-")))}</td>')
        table_already.append(f'<td>{escape(str(item.get("song_title", "-")))}</td>')
        table_already.append(f'<td>{escape((item.get("video_type_original", "") or "").replace("MUSIC_VIDEO_TYPE_", ""))}</td>')
        table_already.append(f'<td>{escape(str(item.get("yt_url", "-")))}</td>')
        table_already.append(f"<td><a target='_blank' href=\"{escape(item.get('path') or '')}\">{escape(item.get('path') or '~No data~')}</a></td>")
        table_already.append("</tr>")

    table_already.append("</tbody>")
    table_already.append("</table>")


    # === Style ===
    style = """
    <style>
        body {
            background-color: lightgray;
            overflow-x: hidden;
            font-family: Arial, Helvetica, sans-serif;
        }
        table {
            border-collapse: collapse;
            text-wrap: nowrap;
        }
        .table-wrapper {
            width: 100%;
            overflow-x: auto;
        }
        th {
            padding: 0.5rem 1rem;
        }
        td {
            padding: 0.2rem 1rem;
            max-width: 200px;
            overflow-x: hidden;
            text-overflow: ellipsis;
        }
        .cell-clone {
            position: fixed;
            overflow: visible;
            z-index: 1000;
            pointer-events: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.5);
        }
        tr:nth-of-type(2n+1) {
            background-color: darkgrey;
        }
        tr:nth-of-type(2n) {
            background-color: lightgrey;
        }
        th {
            background-color: grey;
        }
        code {
            background-color: #eeeeee;
            border-radius: 5px;
            font-family: "Courier New", monospace;
            padding: 0 3px;
        }
        .link-list {
            display: grid;
            grid-template-columns: 220px auto;
            gap: 4px 10px;
        }
    </style>
    """

    # === Scripts ===
    script = r"""

// ### UI ###

// --- Hover cell expand ---
let activeClone = null;

document.querySelectorAll('td').forEach(cell => {
    if (Math.round(cell.getBoundingClientRect().width) >= Math.round(cell.scrollWidth)) {
        return;
    }
    cell.addEventListener('mouseenter', () => {
        const rect = cell.getBoundingClientRect();
        const cell_style = getComputedStyle(cell);
        const row_style = getComputedStyle(cell.parentElement);

        const table = cell.parentElement.parentElement.parentElement; // --- TODO: MAKE MORE EFFICIENT, DONT USE CLOSEST
        const tableRect = table.getBoundingClientRect();

        const clone = cell.cloneNode(true);
        clone.classList.add('cell-clone');

        clone.style.top = rect.top + 'px';
        clone.style.left = rect.left + 'px';
        clone.style.backgroundColor = row_style.backgroundColor;
        clone.style.padding = cell_style.padding;
        clone.style.boxSizing = 'border-box';
        clone.style.textOverflow = 'clip';

        // --- Space available before hitting viewport edge 
        clone.style.top = rect.top + 'px';
        clone.style.left = rect.left + 'px';
        clone.style.backgroundColor = row_style.backgroundColor;
        clone.style.padding = cell_style.padding;
        clone.style.boxSizing = 'border-box';
        clone.style.textOverflow = 'clip';
        clone.style.whiteSpace = 'nowrap';
        clone.style.maxWidth = 'none';

        document.body.appendChild(clone);

        const w_avail = tableRect.right - rect.left;
        const w_needed = clone.scrollWidth;

        if (w_needed > w_avail) {
            // --- doesnt fit
            clone.style.whiteSpace = 'normal';
            clone.style.overflowWrap = 'break-word';
            clone.style.wordBreak = 'break-word';
            clone.style.maxWidth = w_avail + 'px';
            clone.style.minHeight = rect.height + 'px';
        } else {
            // --- fits
            clone.style.minHeight = rect.height + 'px';
        }

        activeClone = clone;

    });

    cell.addEventListener('mouseleave', remove_clone);

});
function remove_clone() {
    if (activeClone) {
        activeClone.remove();
        activeClone = null;
    }
}
window.addEventListener('scroll', remove_clone, true);
window.addEventListener('resize', remove_clone);


// ### Download CSV ###
function download_CSV() {
    const table_select = document.getElementById("csv-table-select");
    const table_select_val = table_select.value;
    const table_select_text = table_select.options[table_select.selectedIndex].text;
    const table = document.getElementById(table_select_val);
    const rows = table.querySelectorAll("tr");
    const csv = [];

    rows.forEach(row => {
        const cols = row.querySelectorAll("th, td");
        const rowData = Array.from(cols).map(col => {
            const url = col.querySelector("a");
            var val;
            if (url) {
                val = url.href;
            } else {
                val = col.innerText.trim();
            }
            return `"${val.replace(/"/g, '""')}"`;
        });

        csv.push(rowData.join(","));
    });

    const csvContent = csv.join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.download = `${filename} ${table_select_text}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}


// ### Check Downloads ###
function check_downloads() {
    console.log("--- Check Downloads ---");
    var table = document.getElementById("table-success");

    const searched_list = Array.from(table.rows).slice(1).map(row => row.cells[2]?.textContent.trim());
    const artists_dl_list = Array.from(table.rows).slice(1).map(row => row.cells[3]?.textContent.trim());
    const titles_dl_list = Array.from(table.rows).slice(1).map(row => row.cells[4]?.textContent.trim());

    var nr_sus = searched_list.length;

    for (let i = 0; i < searched_list.length; i++) {
        const search = searched_list[i];
        const artist = artists_dl_list[i];
        const title = titles_dl_list[i];

        const search_cl = search.toLowerCase().replaceAll("-", "").replaceAll(" ", "");
        const dl_cl = (artist + title).toLowerCase().replaceAll("-", "").replaceAll(" ", "");

        if (search_cl == dl_cl) {
            // --- Exact match
            nr_sus--;
            continue;
        }

        const search_cl_nobr = search_cl.replace(/\([^)]*\)|\[[^\]]*\]/g, "");
        const dl_cl_nobr = dl_cl.replace(/\([^)]*\)|\[[^\]]*\]/g, "");

        if (search_cl_nobr == dl_cl_nobr && search_cl_nobr != "" && dl_cl_nobr != "") {
            // --- Matches except brackets
            console.log(`${search}   <Matches except for brackets>`);
            table.rows[i + 1].title = "Matches except for brackets";
            table.rows[i + 1].style.backgroundColor = "hsl(50, 100%, 80%)";
            continue;
        }

        const search_nobr = search.toLowerCase().replaceAll("-", "").replace(/\([^)]*\)|\[[^\]]*\]/g, "");
        const dl_nobr = (artist + " " + title).toLowerCase().replaceAll("-", "").replace(/\([^)]*\)|\[[^\]]*\]/g, "");
        const jaccard = similarity_jaccard(search_nobr, dl_nobr)
       
        if (jaccard == 1) {
            // --- Matches, but word ordering is wrong
            console.log(`${search}   <Matches, but word ordering is wrong>`);
            table.rows[i + 1].title = "Matches, but word ordering is wrong";
            table.rows[i + 1].style.backgroundColor = "hsl(30, 100%, 75%)";
            continue;
        }
        if (jaccard >= 0.8) {
            // --- Fits, but has been shuffled or missing or wrong words
            console.log(`${search}   <Some words are shuffled, missing, or incorrect. Jaccard = ${jaccard} (1-0, higher is better)>`);
            table.rows[i + 1].title = `Some words are shuffled, missing, or incorrect. Jaccard = ${jaccard} (1-0, higher is better)`;
            table.rows[i + 1].style.backgroundColor = "hsl(20, 100%, 70%)";
            continue;
        }

        const levensht = similarity_levenshtein(search_cl_nobr, dl_cl_nobr)
        console.log(`${search}   <Potentially no match or typos. Levenshtein = ${levensht} (1-0, higher is better)>`);
        table.rows[i + 1].title = `Potentially no match or typos. Levenshtein = ${levensht} (1-0, higher is better)`;
        table.rows[i + 1].style.backgroundColor = `hsl(0, 100%, ${Math.round(levensht * 50 + 30)}%)`;
    }

    console.log("--- Finished Download Check ---")
    document.getElementById("check_results").innerHTML = `Results: ${nr_sus} items may have name mismatches and have been marked. There may be false positives, especially for text queries.
    <ul>
        <li>Not marked: Exact match</li>
        <li>Yellow: Matches except for brackets (Can usually be ignored)</li>
        <li>Orange: Some words are shuffled, missing, or incorrect</li>
        <li>Red: Potential name mismatch or typo. Darker shades indicate lower similarity.</li>
    </ul>
    Hover over the marked rows to show additional information. Reload site to clear colors.<br>
    <i>IMPORTANT: It is normal that there are a lot of mismatches when downloading playlists containing music videos or unofficial lyric videos. A name mismatch does not necessarily mean the wrong song was downloaded. Its just an indication for you where to look.</i>`;
}


// ### Utility ###

var levenshtein = (function() {
    var row2 = [];
    return function(s1, s2) {
        if (s1 === s2) {
            return 0;
        } else {
            var s1_len = s1.length, s2_len = s2.length;
            if (s1_len && s2_len) {
                var i1 = 0, i2 = 0, a, b, c, c2, row = row2;
                while (i1 < s1_len)
                    row[i1] = ++i1;
                while (i2 < s2_len) {
                    c2 = s2.charCodeAt(i2);
                    a = i2;
                    ++i2;
                    b = i2;
                    for (i1 = 0; i1 < s1_len; ++i1) {
                        c = a + (s1.charCodeAt(i1) === c2 ? 0 : 1);
                        a = row[i1];
                        b = b < a ? (b < c ? b + 1 : c) : (a < c ? a + 1 : c);
                        row[i1] = b;
                    }
                }
                return b;
            } else {
                return s1_len + s2_len;
            }
        }
    };
})();

function similarity_levenshtein(s1, s2) {
    var distance = levenshtein(s1, s2);
    var maxLength = Math.max(s1.length, s2.length);
    if (maxLength == 0) {
        return 1;
    }
    return 1 - (distance / maxLength);
}

function similarity_jaccard(a, b) {
    const words_A = new Set(a.split(" "));
    const words_B = new Set(b.split(" "));
    const intersection = [...words_A].filter(x => words_B.has(x));
    const union = new Set([...words_A, ...words_B]);
    return intersection.length / union.size;
}


    """

    # === Add everything together ===

    html_body = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{escape(title)}</title>
        {style}
    </head>
    <body>
        {head}

        <br>
        <hr>
        <h2>Successful Downloads ({len_success}/{len_total})</h2>
        <div class="table-wrapper">
            {''.join(table_success)}
        </div>

        <br>
        <hr>
        <h2>Failed Downloads ({len_failed}/{len_total})</h2>
        <div class="table-wrapper">
            {''.join(table_failed)}
        </div>

        <br>
        <hr>
        <h2>Already Downloaded ({len_already_downloaded}/{len_total})</h2>
        <div class="table-wrapper">
            {''.join(table_already)}
        </div>

        <br>
        <hr>
        <div class="link-list">
            <div>Need more info? Visit:</div>
            <a href="https://github.com/ChemistryGull/SomeDL">https://github.com/ChemistryGull/SomeDL</a>
            <div></div>
            <a href="https://somedl.readthedocs.io/en/latest/index.html">https://somedl.readthedocs.io/en/latest/index.html</a>

            <div>Need help? Ask here:</div>
            <a href="https://github.com/ChemistryGull/SomeDL/discussions">https://github.com/ChemistryGull/SomeDL/discussions</a>

            <div>Tips or ideas? Tell me:</div>
            <a href="https://github.com/ChemistryGull/SomeDL/discussions/categories/ideas">https://github.com/ChemistryGull/SomeDL/discussions/categories/ideas</a>

            <div>Found a bug? Tell me:</div>
            <a href="https://github.com/ChemistryGull/SomeDL/issues">https://github.com/ChemistryGull/SomeDL/issues</a>
            
            <div>Any other feedback? Tell me:</div>
            <a href="https://github.com/ChemistryGull/SomeDL/discussions/categories/feedback">https://github.com/ChemistryGull/SomeDL/discussions/categories/feedback</a>
        
        </div>
        <script>
        const filename = 'Download Report {time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())}'
        {script}
        </script>

    </body>
    </html>
    """

    return html_body




def generateDownloadReport(data, failed, already_downloaded = []):

    html_body = build_download_report(data, failed, already_downloaded)

    filepath = Path(config["download"]["output_dir"]) / Path(f'Download Report {time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())}.html')
    filepath.write_text(html_body, encoding="utf-8")

    # with open(filepath, "w", encoding="utf-8") as f:
    #     f.write(html_body)

    if config["download"]["output_dir"] == ".":
        console.info(f'Download finished! Created download report in this folder')
    else:
        console.info(f'Download finished! Created download report at: {config["download"]["output_dir"]}')


