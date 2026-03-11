<div align="center">
    
# SomeDL - Song+Metadata Downloader

**SomeDL** is a easy to use command-line tool for downloading music with accurate metadata - simple installation and no login or API tokens required!


![SomeDL usage gif](https://github.com/ChemistryGull/SomeDL/blob/main/docs/images/somedl_usage_cut.gif)


The audio is downloaded using yt-dlp, SomeDL accepts text queries, YouTube URLs and YouTube playlist URLs. Metadata is fetched from YouTube, MusicBrainz for genre, Genius and Deezer. No API tokens required, it works out of the box.

</div>

> [!TIP]
> If you have any problems, feature requests, suggestions of improvements of any kind or even general questions, do not hesitate to open an issue here on GitHub. I am open to add functionality based on individual usecase. See [How can I give feedback or make feature requests?](#how-can-i-give-feedback-or-make-feature-requests)

> *Disclaimer: This project - although being fully functional - is primarily a way for me to learn the handling of APIs in python. This program is for educational purposes. SomeDL is developed on Linux and tested on Linux & Windows. This project is was not "vibecoded".*


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
- Download via search query, YouTube URL or YouTube Playlist URL
- Simple installation (And [quick guides](#requirements) for the installation of the dependencies)
- No login or API tokens required
- Complete metadata - way better than just relying on yt-dlp (see [here](#why-should-i-use-somedl-over-yt-dlp) why)
``` 
Song title | Artist name | Album name | High quality cover art (544x544) | Release date (Year) | Track number | Genre | Lyrics | Copyright/Label | ISRC | MusicBrainz artist ID (MBID)
```
- Different output formats: `opus, m4a, mp3, ogg`
- Sort downloads automatically into folders according to a template if desired
    - For example: `{artist}/{artist} - {song}`
    - Or more complex: `{artist}/{year} - {album}/{track_pos} - {song}`
- User configuration file
- Download report - get a quick overview over the downloaded songs, including their metadata.

## Proposed Features
- [ ] Give option to download every song from an album automatically. (*coming soon*)
- [ ] Fallback lyrics source
- [ ] Update metadata in existing files
- [ ] Parallel downloads


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
This software is currently not packaged on any repo. Use your prefered way to install python programs, like for example [pipx](https://pipx.pypa.io/stable/):
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
WARNING - This artist does not have any genre set on MusicBrainz
```

MusicBrainz does not have any genre tags for that artist. Visit [this section](#why-is-the-wrong-genreno-genre-set) on how to add this data to MusicBrainz yourself.

```
WARNING - DEEZER API returned no results. Continuing without Deezer metadata (ISRC, Label)
```
Deezer has not found the song. This may be because of some different spelling or other reaseons. The download will continue without ISRC and music label data.

#### YT-DLP specific warnigs:

```
WARNING: [youtube] No supported JavaScript runtime could be found. Only deno is enabled by default; to use another runtime add –js-runtimes RUNTIME[:PATH] to your command/config. YouTube extraction without a JS runtime has been deprecated, and some formats may be missing. See https://github.com/yt-dlp/yt-dlp/wiki/EJS for details on installing one
```
This warning appears if Deno is not installed properly. Visit [this section](#deno) on how to install deno. 

```
WARNING: [youtube] xHcPUTfPuk0: Some android_vr client https formats have been skipped as they are missing a URL. YouTube may have enabled the SABR-only streaming experiment for the current session. See  https://github.com/yt-dlp/yt-dlp/issues/12482  for more details
```
YouTube is experimenting with different streaming URLs. Random sessions seem to be picked for these experiments, which leads to this warning. This results in no audio-only file being provided, so yt-dlp has to download the video version and extract the audio. Because of the larger file size (15-35 MiB instad of 3-6 MiB), the download will take a bit longer for that song. But besides that, the song will still be downloaded normally.

```
ERROR: Did not get any data blocks
```
Sometimes following the warning above. yt-dlp fixes such data issues automatically in most cases, so the song will still be downloaded as normal. 

```
WARNING: [youtube] [jsc] JS Challenge Provider "deno" returned an invalid response:         response = JsChallengeProviderResponse(request=JsChallengeRequest(type=<JsChallengeType.N: 'n'>, input=NChallengeInput(player_url='https://www.youtube.com/s/player/44899b31/tv-player-ias.vflset/tv-player-ias.js', challenges=['14UbMsOV98OEGPIp1T', '4pHgHqt9lVyQYPVlqs', 'eiQkCMjDm5lNTLFEjf']), video_id='kpxfGeyma1E'), response=None, error='no solutions')
         Please report this issue on  https://github.com/yt-dlp/yt-dlp/issues?q= , filling out the appropriate issue template. Confirm you are on the latest version using  yt-dlp -U
```
This and similar warnings are usually caused by canges by YouTube. The yt-dlp team deals with these problems, updating to the newest yt-dlp version may fix these problems. Usually this will not significally affect song download.

```
ERROR: [youtube] G0rQKudItF4: Sign in to confirm your age. This video may be inappropriate for some users. Use --cookies-from-browser or --cookies for the authentication. See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies. Also see  https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies  for tips on effectively exporting YouTube cookies
ERROR - yt-dlp download failed. Do you have ffmpeg installed? Is the song https://music.youtube.com/watch?v=G0rQKudItF4 age restricted?: ERROR: [youtube] G0rQKudItF4: Sign in to confirm your age. This video may be inappropriate for some users. Use --cookies-from-browser or --cookies for the authentication. See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies. Also see  https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies  for tips on effectively exporting YouTube cookies
ERROR - File was not downloaded successfully with yt-dlp
WARNING - Song was not downloaded properly (or file does already exist)
```
Like mentioned in the error message, this song is age-restricted. Visit [How do I download age restricted songs?](#how-do-i-download-age-restricted-songs) on how to download age-restricted content.



