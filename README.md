# SomeDL - Song+Metadata Downloader
This is a simple commandline program to download Music with the correct metadata.

This project is under heavy developement, this README will be updated soon.


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