<div align="center">
    
# SomeDL - Song+Metadata Downloader


**SomeDL** is a easy-to-use command-line tool for downloading music with accurate metadata. Simple installation and no login or API tokens required! Now also with a WebUI!


[![PyPI version](https://img.shields.io/pypi/pyversions/somedl)](https://pypi.org/project/somedl/)
[![PyPI downloads](https://img.shields.io/pypi/dw/somedl)](https://pypistats.org/packages/somedl)
[![PyPI Version](https://img.shields.io/pypi/v/somedl)](https://pypi.org/project/somedl/)
[![GitHub stars](https://img.shields.io/github/stars/chemistrygull/somedl?style=flat)](https://github.com/ChemistryGull/SomeDL)
[![Last commit](https://img.shields.io/github/last-commit/chemistrygull/somedl)](https://github.com/ChemistryGull/SomeDL)

![SomeDL usage gif](https://github.com/ChemistryGull/SomeDL/blob/main/docs/images/somedl_usage_cut.gif)
![SomeDL WebUI](https://github.com/ChemistryGull/SomeDL/blob/main/docs/images/webui/somedl_webui_download_2.png)


The audio is downloaded using yt-dlp. SomeDL accepts text queries, YouTube URLs and YouTube playlist URLs. Metadata is fetched from YouTube, MusicBrainz, Genius and Deezer. Setlist data is fetched from setlist.fm. No API tokens required for any of these services, it works out of the box.

</div>

> [!TIP]
> If you have any problems, feature requests, suggestions of improvements of any kind or even general questions, do not hesitate to open an issue or start an discussion here on GitHub. I am open to add functionality based on individual usecases. See [How can I give feedback or make feature requests?](https://github.com/ChemistryGull/SomeDL#how-can-i-give-feedback-or-make-feature-requests)

> *Disclaimer: This project - although being fully functional - is primarily a way for me to learn the handling of APIs in python. This program is for educational purposes. SomeDL is developed on Linux and tested on Linux & Windows. This project is human-made, no code from generative AI is used.*

For more information, visit the [SomeDL ReadTheDocs page](https://somedl.readthedocs.io/en/latest/index.html).

# Usage
## CLI
Simply type `somedl` followed by your search query in quotes.
```
somedl "Nirvana - Smells like teen spirit"
```

You can also search by YouTube or YouTube music URL and even by YouTube playlist URL. Search for multiple songs at once by seperating them with spaces.

```
somedl "https://music.youtube.com/watch?v=W0Wo5zhgvpM" "https://music.youtube.com/playlist?list=OLAK5uy_mHURRD4wyePH5Kl8wQkgyfFhbvmK2pYk4" "Iron maiden - run to the hills"

```
Run `somedl -h` to get more information for the different configuration options.

## WebUI
Run `somedl web` in your terminal, a browser window with the SomeDL WebUI will open.


# Features
- Simple usage
- Download via search query, YouTube URL, YouTube Playlist URL and even entire discographies with YouTube Music channel URLs.
- Simple installation with pip (And [quick guides](https://github.com/ChemistryGull/SomeDL#requirements) for the installation of the dependencies).
- No login or API tokens required.
- Complete metadata - way better than just relying on yt-dlp (see [here](https://somedl.readthedocs.io/en/latest/usage/faq.html#why-should-i-use-somedl-over-yt-dlp) why).
``` 
Song title | Artist name | Album name | High quality cover art (544x544) | Release date (Year) | Track number | Genre | Lyrics sycned and plain | Copyright/Label | ISRC | MusicBrainz artist ID (MBID)
```
- Several output formats: `opus, m4a, mp3, ogg, flac`
- Sort downloads automatically into folders according to a template if desired
    - For example: `{album_artist}/{artist} - {song}`
    - Or more complex: `{album_artist}/{year} - {album}/{track_pos} - {song}`
    - You can always change your storage template later with `somedl new-template`
- Add missing metadata to existing music files with `somedl import`
- Download report - get a quick overview over the downloaded songs, including their metadata.
- And much more!

## WebUI
[Here](https://github.com/ChemistryGull/SomeDL/blob/main/docs/webui.md) you can see pictures of the WebUI.

- Download songs directly from a browser-based graphical interface and track the progress
- Search for music within the WebUI using a YouTube Music–style interface.
- Look up concert setlists for bands and artists.
- View download history for the current session
- Change settings directly from the WebUI
- Customize and theme the SomeDL WebUI to match your preferences

## Proposed Features

- [x] Web-UI (*NEW in 1.5.0*)
- [x] Download songs based on concert setlists, part of the new web UI (*NEW in 1.5.0*)

# Installation
This utility can be installed using pip. Also confirm that you meet all the installation [requirements](https://github.com/ChemistryGull/SomeDL#requirements)!
## Windows
```
pip install somedl
```
or
```
py -m pip install somedl
```
To update an existing SomeDL installation, add the `--upgrade` flag tho the command above.


## Linux
This software is currently not packaged in any repository. Install it using your preferred Python package manager, such as [pipx](https://pipx.pypa.io/stable/):
```
pipx install somedl
```
## Requirements
### Python (REQUIRED)
SomeDL is developed and tested on the newest version of Python (currently 3.14). Python 3.10 or newer is required. Visit [How to install python](https://github.com/ChemistryGull/SomeDL/blob/main/docs/how_to_install_python.md)  for a short guide.

### FFmpeg (REQUIRED)
SomeDL uses yt-dlp, which needs [ffmpeg](https://ffmpeg.org/) in order to convert the downloaded audio file to mp3. Visit [How to install ffmpeg](https://github.com/ChemistryGull/SomeDL/blob/main/docs/how_to_install_ffmpeg.md) for a short guide.

### Deno
It is also recommended to have Deno installed. yt-dlp needs deno to work properly (https://github.com/yt-dlp/yt-dlp/wiki/EJS). SomeDL should work without it, but yt-dlp will always print a warning.
- To install deno, go to https://docs.deno.com/runtime/getting_started/installation/
- If you have npm installed, you can use npm to install deno. If not, open PowerShell (not CMD!) and execute the command provided. (This downloads and installs a script, be aware to only do this from trusted sources!)

## Post install
After installing, you can create a configuration file with `somedl --generate-config`. The config file is usually located at:

- Linux:    `~/.config/SomeDL/somedl_config.toml`
- Windows:  `C:\Users\<User>\AppData\Roaming\SomeDL\somedl_config.toml`
- MacOS:    `~/Library/Application Support/SomeDL/somedl_config.toml`

In the config files you can edit the behaviour of SomeDL, like defining an output template, setting default output format & output folder and much more. Inside this config file, there are comments that explain each setting. (For Windows users it is recommended to read and edit the config file with an editor that has syntax highlighing, like Notepad++.).

## How can I give feedback or make feature requests?
- **Bug report**: Open an [issue](https://github.com/ChemistryGull/SomeDL/issues).
- **Feature requests**: Open an [issue](https://github.com/ChemistryGull/SomeDL/issues) or start a discussion in the [ideas](https://github.com/ChemistryGull/SomeDL/discussions/categories/ideas) category.
- **General feedback**: Start a discussion in the [Feedback category](https://github.com/ChemistryGull/SomeDL/discussions/categories/feedback).
- **General question**: Read the [FAQ](#faq) or ask in the [Q&A](https://github.com/ChemistryGull/SomeDL/discussions/categories/q-a) category.
- **Anything else**: Start a discussion in the [general](https://github.com/ChemistryGull/SomeDL/discussions/categories/general) category.

## More information
For more information, FAQ and How To sections, visit the [SomeDL ReadTheDocs page](https://somedl.readthedocs.io/en/latest/index.html).
