<div align="center">
    
# SomeDL - Song+Metadata Downloader


**SomeDL** is a easy-to-use command-line tool for downloading music with accurate metadata - simple installation and no login or API tokens required!


[![PyPI version](https://img.shields.io/pypi/pyversions/somedl)](https://pypi.org/project/somedl/)
[![PyPI downloads](https://img.shields.io/pypi/dw/somedl)](https://pypistats.org/packages/somedl)
[![PyPI Version](https://img.shields.io/pypi/v/somedl)](https://pypi.org/project/somedl/)
[![GitHub stars](https://img.shields.io/github/stars/chemistrygull/somedl?style=flat)](https://github.com/ChemistryGull/SomeDL)
[![Last commit](https://img.shields.io/github/last-commit/chemistrygull/somedl)](https://github.com/ChemistryGull/SomeDL)

![SomeDL usage gif](https://github.com/ChemistryGull/SomeDL/blob/main/docs/images/somedl_usage_cut.gif)


The audio is downloaded using yt-dlp. SomeDL accepts text queries, YouTube URLs and YouTube playlist URLs. Metadata is fetched from YouTube, MusicBrainz, Genius and Deezer. No API tokens required for any of these services, it works out of the box.

</div>

> [!TIP]
> If you have any problems, feature requests, suggestions of improvements of any kind or even general questions, do not hesitate to open an issue or start an discussion here on GitHub. I am open to add functionality based on individual usecases. See [How can I give feedback or make feature requests?](#how-can-i-give-feedback-or-make-feature-requests)

> *Disclaimer: This project - although being fully functional - is primarily a way for me to learn the handling of APIs in python. This program is for educational purposes. SomeDL is developed on Linux and tested on Linux & Windows. This project is not vibecoded.*


# Usage
Simply type `somedl` followed by your search query in quotes.
```
somedl "Nirvana - Smells like teen spirit"
```

You can also search by YouTube or YouTube music URL and even by YouTube playlist URL. Search for multiple songs at once by seperating them with spaces.

```
somedl "https://music.youtube.com/watch?v=W0Wo5zhgvpM" "https://music.youtube.com/playlist?list=OLAK5uy_mHURRD4wyePH5Kl8wQkgyfFhbvmK2pYk4" "Iron maiden - run to the hills"

```
Run `somedl -h` to get more information for the different configuration options.

# Features
- Simple usage
- Download via search query, YouTube URL, YouTube Playlist URL and even entire discographies with YouTube Music channel URLs.
- Simple installation with pip (And [quick guides](#requirements) for the installation of the dependencies).
- No login or API tokens required.
- Complete metadata - way better than just relying on yt-dlp (see [here](#why-should-i-use-somedl-over-yt-dlp) why).
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

## Proposed Features
- [x] Download archive (*New in v1.3.0!*)
- [x] Downloading entire discographies with YouTube Music channel URLs (*New in v1.3.0!*)
- [ ] Web-UI (*Work in progress*)
- [ ] Download songs based on concert setlists

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
To update an existing SomeDL installation, add the `--upgrade` flag tho the command above.


## Linux
This software is currently not packaged in any repository. Install it using your preferred Python package manager, such as [pipx](https://pipx.pypa.io/stable/):
```
pipx install somedl
```
## Requirements
### Python (REQUIRED)
SomeDL is developed and tested on the newest version of Python (currently 3.14). Python 3.10 is required. Visit [How to install python](docs/how_to_install_python.md) for a short guide.

### FFmpeg (REQUIRED)
SomeDL uses yt-dlp, which needs [ffmpeg](https://ffmpeg.org/) in order to convert the downloaded audio file to mp3. Visit [How to install ffmpeg](docs/how_to_install_ffmpeg.md) for a short guide.

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

# How-To
### Whats the way to get the best metadata?
If you want the most accurate metadata, especially album name, it is best practice to download songs with YouTube Muisc album URLs, or by using the `--fetch-album` flag. Downloading an entire album this way ensures that all songs in that album get the same album name, and the songs are not split between the regular version "extended editon" and "deluxe edition" variations.

### How can i download an entire album with just a search query?
You can use the `--fetch-album` flag. With this flag set, SomeDL downloads the entire album of every song in the download queue. You can also provide a YouTube Music URL to the album.

### How can i download all songs from an artist?
You can use the `--fetch-album` flag. With this flag set, SomeDL downloads the entire album of every song in the download queue. 

### How can I change configurations?
Generate a SomeDL-config file with
```
somedl --generate-config
```
Then edit the `somedl_config.toml` file on the path it prints out. Inside this configuration file, there are comments that explain each setting.

### How can i avoid redownloading files when removing them from the download folder?
You can use the download archive for this. Define a download archive file with `--downlaod archive /path/to/archive.txt` or by changing the `download_archive` config. The name and filetype of the archive do not matter. When such a file is defined, all video IDs of successfull downloads will be added into that download archive and will be skipped on any future download attempts.

If you want to download a song that has already been downloaded with the download_archive enabled, use the `--redownload` flag to download a song.

### How can i change the output template for already downloaded files?
You can type `somedl new-template` into the terminal. It will ask you to provide the path to your files and the path to a new folder. You will also have to provide the new output template. You can choose between moving the files (less SSD writes) and copying files (safer in case something goes wrong). You can also merge different storage template in this way. 

### How can i add metadata to already downloaded files?
If you already have a library of songs downloaded with yt-dlp or other downloaders, you can use the `somedl import` utility. It will ask you to provide the path to your files and the path to a new folder, or your SomeDL library. You will also have to provide the new output template, and what import mode you want to choose. Import modes are:
- copy: Oiginal files are left in place (Recommended unless you have a backup and know what you are doing)
- move: original files are deleted after import
- update: Just update the metadata of the original files. This will neither change the filename nor move the file, but change the original file metadata itself. Use copy if you want to keep the original files.

Then you will have to choose the mode of metadata detection. SomeDL has to figure out what each song is. There are different strategies to do so:

- A) YouTube video ID in the filename (e.g. The Cold [xI91NneSY5Y].mp3)
- B) A "Artist - Song" file naming scheme
- C) Infering from existing metadata.

Choose the mode that fits best for your usecase. Do you have many songs downloaded with yt-dlp and still have the 11-digit Video ID [xI91NneSY5Y]? Type yes for option A. Do all your files follow a "Artist - Song" file naming scheme? Type yes for option B. Do you know your files have valid metadata (only Artist name and Song name are needed)? Choose option C. You can also combine options, like A and C or A and B. You cannot combine B with C!

After that, you can start with the import. It is best to first test the import on a smaller folder.



# FAQ
### How can I give feedback or make feature requests?
- **Bug report**: Open an [issue](https://github.com/ChemistryGull/SomeDL/issues).
- **Feature requests**: Open an [issue](https://github.com/ChemistryGull/SomeDL/issues) or start a discussion in the [ideas](https://github.com/ChemistryGull/SomeDL/discussions/categories/ideas) category.
- **General feedback**: Start a discussion in the [Feedback category](https://github.com/ChemistryGull/SomeDL/discussions/categories/feedback).
- **General question**: Read the [FAQ](#faq) or ask in the [Q&A](https://github.com/ChemistryGull/SomeDL/discussions/categories/q-a) category.
- **Anything else**: Start a discussion in the [general](https://github.com/ChemistryGull/SomeDL/discussions/categories/general) category.

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

*Genre info is added per artist to the song, meaning all songs of the same artist get the same genre. Music brainz does have genre tags per album and even per song, but since they are crowdsourced, they are often incomplete, so it is best to stick with the artists tags.*

### How do I download age restricted songs?
You need to be logged into your age-verified YouTube account inside your browser. Then, append `--cookies-from-browser firefox` to your SomeDL command. This only works properly for non-chromium based browsers and I recommend to use firefox for this. For chromium based browsers, there is also the option of exporting a cookie file from your browser and appending that with `--cookies "/path/to/file/cookies.txt`. Only add these flags when downloading age restricted content. Heavy use of this application may lead to your account being banned when adding your browser cookies. This is a yt-dlp specific issue, visit their official documentation for more info. https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp

### What is that "Download Report .... .html" file?
With every download of more than one song, a download report is created. You can open it in any browser. This is a quick overview of what metadata was downloaded and gives you a fast and easy way to check if there is something wrong.

### How long does a song download take?
Usually arount 3-4 seconds per song when downloading a list of 10+ songs at the same time with default concurrency. It takes 8-10 seconds to download a single song. If you increase concurrency, you can increase the speed to up to 2 seconds per song, but do so cautiously as youtube might get your IP rate restricted or temporarily banned if you abuse fast downloads with large lists of songs. 

### What does the error message/warning ... mean?
```
WARNING - Video has no song ID - this might be a regular YouTube video, not a song.
```
This video is not listed as a song on youtube. This is the case for most regular videos on youtube. There is no metadata to fetch. It may be a song that has been uploaded by a very small creator (e.g. a fan song), in which case you will have to download the song using yt-dlp and add the metadata manually. 


#### YT-DLP specific warnigs:

```
WARNING - >_yt-dlp: [youtube] No supported JavaScript runtime could be found. Only deno is enabled by default; to use another runtime add –js-runtimes RUNTIME[:PATH] to your command/config. YouTube extraction without a JS runtime has been deprecated, and some formats may be missing. See https://github.com/yt-dlp/yt-dlp/wiki/EJS for details on installing one
```
This warning appears if Deno is not installed properly. Visit [this section](#deno) on how to install deno. 

```
WARNING - >_yt-dlp: [youtube] xHcPUTfPuk0: Some android_vr client https formats have been skipped as they are missing a URL. YouTube may have enabled the SABR-only streaming experiment for the current session. See  https://github.com/yt-dlp/yt-dlp/issues/12482  for more details
```
YouTube is experimenting with different streaming URLs. Random sessions seem to be picked for these experiments, which leads to this warning. This results in no audio-only file being provided, so yt-dlp has to download the video version and extract the audio. Because of the larger file size (15-35 MiB instad of 3-6 MiB), the download will take a bit longer for that song. But besides that, the song will still be downloaded normally.

```
ERROR - >_yt-dlp: Did not get any data blocks
```
Sometimes following the warning above. yt-dlp fixes such data issues automatically in most cases, so the song will still be downloaded as normal. 

```
WARNING - >_yt-dlp: [youtube] [jsc] JS Challenge Provider "deno" returned an invalid response:         response = JsChallengeProviderResponse(request=JsChallengeRequest(type=<JsChallengeType.N: 'n'>, input=NChallengeInput(player_url='https://www.youtube.com/s/player/44899b31/tv-player-ias.vflset/tv-player-ias.js', challenges=['14UbMsOV98OEGPIp1T', '4pHgHqt9lVyQYPVlqs', 'eiQkCMjDm5lNTLFEjf']), video_id='kpxfGeyma1E'), response=None, error='no solutions')
         Please report this issue on  https://github.com/yt-dlp/yt-dlp/issues?q= , filling out the appropriate issue template. Confirm you are on the latest version using  yt-dlp -U
```
This and similar warnings are usually caused by canges by YouTube. The yt-dlp team deals with these problems, updating to the newest yt-dlp version may fix these problems. Usually this will not significally affect song download.

```
ERROR - >_yt-dlp: [youtube] G0rQKudItF4: Sign in to confirm your age. This video may be inappropriate for some users. Use --cookies-from-browser or --cookies for the authentication. See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies. Also see  https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies  for tips on effectively exporting YouTube cookies
ERROR - >_yt-dlp: yt-dlp download failed. Do you have ffmpeg installed? Is the song https://music.youtube.com/watch?v=G0rQKudItF4 age restricted?: ERROR: [youtube] G0rQKudItF4: Sign in to confirm your age. This video may be inappropriate for some users. Use --cookies-from-browser or --cookies for the authentication. See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies. Also see  https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies  for tips on effectively exporting YouTube cookies
ERROR - >_yt-dlp: File was not downloaded successfully with yt-dlp
WARNING - Song was not downloaded properly
```
Like mentioned in the error message, this song is age-restricted. Visit [How do I download age restricted songs?](#how-do-i-download-age-restricted-songs) on how to download age-restricted content.



