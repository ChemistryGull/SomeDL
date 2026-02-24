# Changelog
https://keepachangelog.com/en/1.1.0/

## [0.2.0]
### Overview:
You can now download age restricted videos by providing --cookies-from-browser followed by the name of your browser where you are logged into youtube with an age verified account.
Download reports are only generated if more than one song inputs are present. When setting the -R flag, the download report is always generated.

### Added
- Add support for downloading age restricted songs by supporting the --cookies-from-browser BROWSER flag or the --cookies flag.
- Add --no-musicbrainz flag to download songs without fetching musicbrainz data (Genre). This can be used when the musicbrainz API causes problems.
- Add download time to download report
- Add --version flag
- Add integrated version check. Runs with every command.

### Fixed
- DownloadError was not properly importet from yt-dlp
- Fix bug, where adding metadata would fail if a previous search of the same artist that yielded no musicbrainz info (because --no-musicbrainz was set) would result in an Invalid MultiSpec data: None error. Added empty string as exception value of .get instead of None
- Returne false if file was not downloaded properly to put the song into the failed list

### Changed
- Download reports 
- Lowered failed download log level to ERROR instead of CRITICAL
- Added informative suggestions (age restriction, ffmpeg) to error message
- Switched recording and artist in the musicbrainz API prompt (new prompt: https://musicbrainz.org/ws/2/recording/?query=artist:"{artist}" AND recording:"{song}"&fmt=json). Having it the other way round prioritizes recording names over artist names.
- Changed 5 seconds musicbrainz timeout to 5 + retry_coundter^2 to wait longer if more retries are needed.

## [0.1.2]
### Changed
- Only add copyright info to metadata if label and date info is present
- Update f-Strings to work in python 3.10 (No nestet quotes of the same type)

## [0.1.1] - 2026.02.22
### Changed
- Set Musicbrainz API retry log to WARNING instead of ERROR
- Changed yt-dlp download error message to hint at installing ffmpeg
- Changed : to - in Download Report naming to make it compatible with Windows
- Updated musicbrainz useragent to current app name

## [0.1.0] - 2026.02.22

- First realease with basic functionality