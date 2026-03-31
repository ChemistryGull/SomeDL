import json
import time
from html import escape
from pathlib import Path

import SomeDL.utils.console as console
from SomeDL.utils.config import config

def generateDownloadReport(data, failed, already_downloaded = []):
    # with open('getPlaylist_data_3.json', 'r', encoding="utf-8") as file:
    #     data = json.load(file)

    #print(json.dumps(data, indent=4, sort_keys=True))

    len_success = len(data)
    len_failed = len(failed)
    len_already_downloaded = len(already_downloaded)
    len_total = len_success + len_failed + len_already_downloaded
    
    #table = "Oh no..."
    title = "Playlist download report"

    parts = [f'<h1>Download Report {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}</h1>']
    parts.append("<p><i>Don't want these download reports? Disable them with </i><code>somedl --disable-report</code></p>")
    
    parts.append(f"<p>Summary: Out of {len_total} songs, {len_success} were downloaded successfully, {len_failed} songs failed to download and {len_already_downloaded} songs were already present.</p>")

    parts.append(f"<p>Songs that were successfully downloaded: ({len_success}/{len_total})</p>")
    parts.append("<table>")

    relevant_keys = [
        ["Artist", "artist_name"],
        ["Title", "song_title"],
        ["Album", "album_name"],
        ["Year", "date"],
        ["Genre", "mb_genres"],
        ["Track", "!special"],
        ["Lyrics", "!special"],
        ["Video Type", "video_type_original"],
        ["URL", "!special"],
        ["Albumart", "!special"],
        ["Download time", "total_time"],
        ["Filetype", "filetype"]
    ]

    # Header
    parts.append("<thead><tr>")
    for header in relevant_keys:
        parts.append(f'<th>{escape(str(header[0]))}</th>')
    parts.append("</tr></thead>")

    # Body
    parts.append("<tbody>")
    for item in data:
        parts.append("<tr>")
        for header in relevant_keys:
            if header[1] == "!special":
                match header[0]:
                    case "Lyrics":
                        if item.get("instrumental"):
                            parts.append(f"<td>Instrumental</td>")
                        elif item.get("lyrics_synced") and item.get("lyrics_plain") and config["metadata"]["lyrics_type"] == "both":
                            parts.append(f"<td>Synced&Plain</td>")
                        elif item.get("lyrics_synced") and config["metadata"]["lyrics_type"] in ["both", "synced", "synced_if_available"]:
                            parts.append(f"<td>Synced</td>")
                        elif item.get("lyrics_plain") and config["metadata"]["lyrics_type"] in ["both", "plain", "synced_if_available"]:
                            parts.append(f"<td>Plain</td>")
                        else: 
                            parts.append(f"<td>No</td>")
                    case "Albumart":
                        if not item.get("album_art"):
                            parts.append(f"<td></td>")
                        elif not len(item.get("album_art", [{}])) == 0:
                            album_art_url = item.get("album_art", [{}])[-1].get("url")
                            parts.append(f"<td><a target='_blank' href={escape(album_art_url)}>Yes</a></td>")
                        else:
                            parts.append(f"<td>No</td>")
                    case "URL":
                        if not item.get("yt_url"):
                            parts.append(f"<td></td>")
                        else:
                            yt_url = item.get("yt_url")
                            parts.append(f"<td><a target='_blank' href={escape(yt_url)}>{escape(yt_url.replace('https://music.youtube.com/watch?v=', '').replace('https://www.youtube.com/watch?v=', ''))}</a></td>")
                    case "Track":
                        trackof = f'{item.get("track_pos")}/{item.get("track_count")}'
                        parts.append(f"<td>{escape(trackof)}</td>")




            else:
                parts.append(f'<td>{escape(str(item.get(header[1], "~No data~")))}</td>')
        parts.append("</tr>")
    parts.append("</tbody>")

    # === Failed ===

    parts.append("</table>")
    parts.append("<br>")
    parts.append("<hr>")
    parts.append("<br>")

    parts.append(f"<p>Songs that failed to download: ({len_failed}/{len_total})</p>")

    parts.append("<table>")

    parts.append("<thead><tr>")
    parts.append("<th>Input Query</th>")
    parts.append("<th>Artist Name</th>")
    parts.append("<th>Song Name</th>")
    parts.append("<th>Video Type</th>")
    parts.append("<th>Youtube URL</th>")

    parts.append("</tr></thead>")

    parts.append("<tbody>")

    for item in failed:
        parts.append("<tr>")
        parts.append(f'<td>{escape(str(item.get("text_query", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("artist_name", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("song_title", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("video_type", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("yt_url", "-")))}</td>')
        parts.append("</tr>")
    parts.append("</tbody>")

    parts.append("</table>")
    
    parts.append("<br>")
    parts.append("<hr>")
    parts.append("<br>")


    # === Already downloaded ===

    parts.append(f"<p>Songs that were already downloaded: ({len_already_downloaded}/{len_total})</p>")

    parts.append("<table>")

    parts.append("<thead><tr>")
    parts.append("<th>Input Query</th>")
    parts.append("<th>Artist Name</th>")
    parts.append("<th>Song Name</th>")
    parts.append("<th>Video Type</th>")
    parts.append("<th>Youtube URL</th>")

    parts.append("</tr></thead>")

    parts.append("<tbody>")

    for item in already_downloaded:
        parts.append("<tr>")
        parts.append(f'<td>{escape(str(item.get("text_query", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("artist_name", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("song_title", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("video_type", "-")))}</td>')
        parts.append(f'<td>{escape(str(item.get("yt_url", "-")))}</td>')
        parts.append("</tr>")
    parts.append("</tbody>")

    parts.append("</table>")


    # === Add everything together ===
    
    table = "".join(parts)

    html_body = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{escape(title)}</title>
        <style>
            table {{
                border-collapse: collapse;
            }}
            th, td {{
                padding: 8px 12px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .item-failed {{
                background-color: #FF3333;
            }}
            code {{
                background-color: #eeeeee;
                border-radius: 3px;
                font-family: "Courier New", monospace;
                padding: 0 3px;
            }}
            .link-list {{
                display: grid;
                grid-template-columns: 220px auto;
                gap: 4px 10px;
            }}
        </style>
    </head>
    <body>
    {table}
    <br>
    <hr>
    <br>
    <div class="link-list">
        <div>Need more info? Visit:</div>
        <a href="https://github.com/ChemistryGull/SomeDL">https://github.com/ChemistryGull/SomeDL</a>

        <div>Need help? Ask here:</div>
        <a href="https://github.com/ChemistryGull/SomeDL/discussions">https://github.com/ChemistryGull/SomeDL/discussions</a>

        <div>Tips or ideas? Tell me:</div>
        <a href="https://github.com/ChemistryGull/SomeDL/discussions/categories/ideas">https://github.com/ChemistryGull/SomeDL/discussions/categories/ideas</a>

        <div>Found a bug? Tell me:</div>
        <a href="https://github.com/ChemistryGull/SomeDL/issues">https://github.com/ChemistryGull/SomeDL/issues</a>
        
        <div>Any other feedback? Tell me:</div>
        <a href="https://github.com/ChemistryGull/SomeDL/discussions/categories/feedback">https://github.com/ChemistryGull/SomeDL/discussions/categories/feedback</a>
      
    </div>
    </body>
    </html>
    """

    filepath = Path(config["download"]["output_dir"]) / Path(f'Download Report {time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())}.html')
    filepath.write_text(html_body, encoding="utf-8")

    # with open(filepath, "w", encoding="utf-8") as f:
    #     f.write(html_body)

    if config["download"]["output_dir"] == ".":
        console.info(f'Download finished! Created download report in this folder')
    else:
        console.info(f'Download finished! Created download report at: {config["download"]["output_dir"]}')


