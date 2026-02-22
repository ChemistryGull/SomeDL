# SomeDL - Song+Metadata Downloader
This is a simple commandline program to download music with the correct metadata.

This project is under heavy developement, this README will be updated soon.

# Usage
Simply type `somedl` followed by your search query in quotes. You typically find 
```
somedl "Nirvana - Smells like teen spirit"
```
You can also search by YouTube or YouTube music URL and even by YouTube playlist URL.

# Installation
This utility can be installed using pip.
## Windows
```
pip install somedl
```
or
```
py -m pip install somedl
```
This expects you to have [ffmpeg](https://ffmpeg.org/) already installed as it is a requirement for yt-dlp to convert the audio files to .mp3. You can verify that you have ffmpeg installed by typing ffmpeg in the commandline. You can install ffmpeg either via winget (more info [here](https://www.gyan.dev/ffmpeg/builds/)) or manually by following a tutorial like [this one](https://www.youtube.com/watch?v=JR36oH35Fgg).

## Linux
This software is currently not packaged in any packagemanager or third party repo. Use your prefered way to install pythograms, like for example [pipx](https://pipx.pypa.io/stable/):
```
pipx install somedl
```


# FAQ
## Why does it download the wrong version of the song?
Rarely a "radio version" or similar has more views than the original version, meaning it is the first result that comes up and therefore the song that gets downloaded by SomeDL. Possible ways to get the correct song:
- Add e.g. "Original" to your search query, for example "Nirvana - Smells like teen spirit original". This might result in the correct song getting downloaded
- Search for the song on youtube music and download by URL. (IMPORTANT: Always use the link of the original soundtrack! Do not use the music video version, this does not have the correct metadata and audio track, so SomeDL has to search youtube again by artist name and song title, resulting in the same issue)

