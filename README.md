# SomeDL - Song+Metadata Downloader
This is a simple commandline program to download music with the correct metadata. The audio is downloaded using yt-dlp. Metadata is fetched from YouTube, but also from different other sources, like MusicBrainz for genre, Genius for album info and Deezer for music label and isrc-codes. All these APIs work without the need for an API token, so you can use this application as is.

**If you have any problems, feature requests, suggestions of improvements of any kind or even general questions, do not hesitate to open an issue here on GitHub. I am open to add functionality based on individual usecase.**

*Disclaimer: This project - although being fully functional - is primarily a way for me to learn the handling of APIs in python. This program is for educational purposes. This software is developed on Linux and tested on Linux & Windows.*

# Usage
Simply type `somedl` followed by your search query in quotes.
```
somedl "Nirvana - Smells like teen spirit"
```
You can also search by YouTube or YouTube music URL and even by YouTube playlist URL. It is also possible to download multiple songs at the same time, like this:
```
somedl "https://music.youtube.com/..." "Delain - Moth to a Flame" "https://music.youtube.com/playlist?list=OLAK5uy_nHlwZujC7fzEgTnKdakqBzO7MIP9sZW48"
```

# Installation
This utility can be installed using pip. Also confirm that you meet all the installation [requirements](#requirements)!
## Windows
```
pip install somedl
```
or
```
py -m pip install somedl
```

## Linux
This software is currently not packaged in any packagemanager or third party repo. Use your prefered way to install pythograms, like for example [pipx](https://pipx.pypa.io/stable/):
```
pipx install somedl
```
## Requirements
### Python (REQUIRED)
This program is developed and testet on the newest version of Python (currently 3.14). So python 3.14 would be recommended, although it probably also works on some older versions. Visit [How to install python](docs/how_to_install_python.md) for a short guide.

### FFmpeg (REQUIRED)
This program uses yt-dlp, which needs [ffmpeg](https://ffmpeg.org/) in order to convert the downloaded audio file to mp3. Visit [How to install ffmpeg](docs/how_to_install_ffmpeg.md) for a short guide.

### Deno
It is also recommended to have Deno installed. yt-dlp needs deno to work properly (https://github.com/yt-dlp/yt-dlp/wiki/EJS). SomeDL should work without it, but yt-dlp will always print a warning.
- To install deno, go to https://docs.deno.com/runtime/getting_started/installation/
- If you have npm installed, you can use npm to install deno. If not, open PowerShell (not CMD!) and execute the command provided. (This downloads and installs a script, be aware to only do this from trusted sources!)

# FAQ
### Why is the wrong version of the song downloaded?
Rarely a "radio version" or similar has more views than the original version, meaning it is the first result that comes up and therefore the song that gets downloaded by SomeDL. Possible ways to get the correct song:
- Add e.g. "Original" to your search query, for example "Nirvana - Smells like teen spirit original". Sometimes this results in the correct song being downloaded. 
- Search for the song on youtube music and download by URL. (IMPORTANT: Always use the link of the original soundtrack! Do not use the music video version, this does not have the correct metadata and audio track, so SomeDL has to search youtube again by artist name and song title, resulting in the same issue)

If you do not not use a non-music-video YouTube Music URL, you are always at the mercy of the youtube search algorythm. But this search is accurate over 95% of the time.

### Why is the wrong genre/no genre set? 
SomeDL gets the genre info from MusicBrainz (Neither YouTube nor Genius provide genre info via their APIs). The genre data on MusicBrainz is crowdsourced. Therefore, some artists may not have a genre set, some may have the wrong genre set. Everyone can create an account on MusicBrainz and vote for the genre (called „tags“). You are invited to do so and help make the database more complete. Please do so responsibly.

*Genre info is added per artist to the song, meaning all songs of the same artist get the same genre. Music brainz does have genre tags per album and even per song, but since they are crowdsourced, they are often incomplete, so it is best to stick with the artists tags*

### How do I download age restricted songs?
You need to be logged into your age-verified YouTube account inside your browser. Then, append `--cookies-from-browser firefox` to your somedl command. This only works properly for non-chromium based browsers and i recommend to use firefox for this. For chromium based browsers, there is also the option of exporting a cookie file from your browser and appending that with `--cookies "/path/to/file/cookies.txt`. Only add these flags when downloading age restricted content. Heavy use of this application may lead to your account being banned when adding your browser cookies. This is a yt-dlp specific issue, visit their official documentation for more info. https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp

