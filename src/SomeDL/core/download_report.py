import json
import time
from html import escape
from pathlib import Path

from SomeDL.utils.logging import log, printj
from SomeDL.utils.config import config

def generateDownloadReport(data, failed):
    # with open('getPlaylist_data_3.json', 'r', encoding="utf-8") as file:
    #     data = json.load(file)

    #print(json.dumps(data, indent=4, sort_keys=True))

    
    #table = "Oh no..."
    title = "Playlist download report"

    parts = [f'<h1>Download Report {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}</h1>']
    parts.append("<p><i>Don't want these download reports? Disable them with </i><code>somedl --disable-report</code></p>")
    parts.append("<p>Songs that were successfully downloaded:</p>")
    parts.append("<table>")

    relevant_keys = [
        ["Artist", "artist_name"],
        ["Title", "song_title"],
        ["Album", "album_name"],
        ["Date", "date"],
        ["Genre", "mb_genres"],
        ["Track", "track_pos"],
        ["...Of", "track_count"],
        ["Lyrics", "!special"],
        ["Video Type", "original_type"],
        ["URL", "yt_url"],
        ["Albumart", "!special"],
        ["Download time", "download_time"],
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
                        has_lyrics = item.get("lyrics")
                        if has_lyrics:
                            parts.append(f"<td>Yes</td>")
                        else: 
                            parts.append(f"<td>No</td>")
                    case "Albumart":
                        if not len(item.get("album_art", [{}])) == 0:
                            album_art_url = item.get("album_art", [{}])[-1].get("url")
                            parts.append(f"<td><a target='_blank' href={escape(album_art_url)}>Yes</a></td>")
                        else:
                            parts.append(f"<td>No</td>")

            else:
                parts.append(f'<td>{escape(str(item.get(header[1], "~No data~")))}</td>')
        parts.append("</tr>")
    parts.append("</tbody>")


    parts.append("</table>")
    parts.append("<br>")
    parts.append("<hr>")
    parts.append("<br>")

    parts.append("<p>Songs that failed to download or were already present:</p>")

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
        log.info(f'Download finished! Created download report in this folder')
    else:
        log.info(f'Download finished! Created download report at: {config["download"]["output_dir"]}')


