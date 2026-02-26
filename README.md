# SomeDL - Song+Metadata Downloader
This is a simple commandline program to download music with the correct metadata. The audio is downloaded using yt-dlp. Metadata is fetched from YouTube, but also from different other sources, like MusicBrainz for genre, Genius for album info and Deezer for music label and isrc-codes. All these APIs work without the need for an API token, so you can use this application as is.

**If you have any problems, feature requests, suggestions of improvements of any kind or even general questions, do not hesitate to open an issue here on GitHub. I am open to add functionality based on individual usecase.**

*Disclaimer: This project - although being fully functional - is primarily a way for me to learn the handling of APIs in python. This program is for educational purposes. This software is developed on Linux and tested on Linux & Windows.*

# Features
- Simple usage
- Simple installation (And [quick guides](#requirements) for the installation of the dependencies)
- No login or API tokens required
- Complete metadata - way better than just relying on yt-dlp (see [here](#why-should-i-use-somedl-over-yt-dlp) why)
    - Song title
    - Artist name
    - Album name
    - High quality cover art (544x544)
    - Release date (Year)
    - Track number
    - Genre
    - Lyrics
    - Copyright/Label
    - ISRC
    - MusicBrainz artist ID (MBID)

# Usage
Simply type `somedl` followed by your search query in quotes.
```
somedl "Nirvana - Smells like teen spirit"
```

You can also search by YouTube or YouTube music URL and even by YouTube playlist URL. Search for multiple songs at once by seperating them with spaces.

```
somedl "https://music.youtube.com/watch?v=W0Wo5zhgvpM" "https://music.youtube.com/playlist?list=OLAK5uy_mHURRD4wyePH5Kl8wQkgyfFhbvmK2pYk4" "Iron maiden - run to the hills"

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
This program is developed and testet on the newest version of Python (currently 3.14). This program requires Python 3.10 or newer, but Python 3.14 is recommended. Visit [How to install python](docs/how_to_install_python.md) for a short guide.

### FFmpeg (REQUIRED)
This program uses yt-dlp, which needs [ffmpeg](https://ffmpeg.org/) in order to convert the downloaded audio file to mp3. Visit [How to install ffmpeg](docs/how_to_install_ffmpeg.md) for a short guide.

### Deno
It is also recommended to have Deno installed. yt-dlp needs deno to work properly (https://github.com/yt-dlp/yt-dlp/wiki/EJS). SomeDL should work without it, but yt-dlp will always print a warning.
- To install deno, go to https://docs.deno.com/runtime/getting_started/installation/
- If you have npm installed, you can use npm to install deno. If not, open PowerShell (not CMD!) and execute the command provided. (This downloads and installs a script, be aware to only do this from trusted sources!)

# FAQ

### Why should I use SomeDL over yt-dlp?
yt-dlp has the ability to add metadata and thumbnails with the flags `--embed-metadata` and `--embed-thumbnail`. However, this data is incomplete and a often mess. Examples:
- No genre data (it puts "Music" as the genre)
- Embeds rectangular thumbnail instead of square cover art
- Does not include Lyrics
- Often treats songs as singles, even though they are part of an album (leading to a wrong album name and a wrong thumbnail)
- Wrong date (Often uses upload date instead of release date of the song)
- No track number
yt-dlp is not a song downloader with complete metadata support (and does not claim to be). Thats why someDL uses multiple different sources to get the most accurate metadata possible.

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

### What is that "Download Report .... .html" file?
With every download of more than one song, a download report is created. This is a quick overview of what metadata was downloaded and gives you the ability to check if there is something wrong.

### How long does a song download take?
Usually arount 10 seconds per song. 5-6 seconds are the yt-dlp download and conversion to mp3, 4-5 seconds are the fetching of the metadata.

### What does the error message/warning ... mean?
```
WARNING - Video "TITLE OF THE VIDEO" is likely not a song. Skipping
```
This video is not listed as a song on youtube. This is the case for most regular videos on youtube. There is no metadata to fetch. It may be a song that has been uploaded by a very small creator (e.g. a fan song), in which case you will have to download the song using yt-dlp and add the metadata manually. 


```
WARNING - Musicbrainz GetSongByName Request failed. Retrying after 5 seconds. 3 attempts left. ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')) 
```
MusicBrainz limits the rate at which apps like SomeDL can access their servers. If there are to many requests in a short time, some are denied. Usually a retry 5-10 seconds later will be successful and the download can continue.

```
WARNING - Fetching MusicBrainz song failed. Continuing without MusicBrainz metadata (MBID, Genre)
```

If MusicBrainz cannot find that artist, this warning appears. No genre data is added.

```
WARNING - MusicBrainz has found no genre
```

MusicBrainz does not have any genre tags for that artist. Visit [this section](#why-is-the-wrong-genreno-genre-set) on how to add this data to MusicBrainz yourself.

