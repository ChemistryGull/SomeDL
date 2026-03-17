# Changelog
https://keepachangelog.com/en/1.1.0/


## [1.1.3] - 17.03.2026

### Changed
- When a URL contains both song (v=) and playlist (list=) IDs, now only the song is downloaded, not the whole list by default
    - Added a user info prompt when this case appears.
    - Why song only as default? For these types of URLs, its not always clear what the user preferes. Just downloading one song is less bad when its the wrong desicion than downloading the whole playlist would be. 
- Add `--get-song` and `--get-playlist` flags for the above change.
- Add `prefer_playlist` config (default false)
- Changed `Song does already exist. Skipping download` Warning to Info and colored green. Temporary until i implement a better return value.


## [1.1.2] - 16.03.2026

### Added
- Add support for `/browse/` url - containting playlists and albums. The latter got its own fetching function

### Fixed
- Playlists of any sized can now be processed, as the limit of 200 (or 100 according to docs) tracs has been removed by adding `limit=None`.
- Add Python 3.14 to the classifies. I forgot it with the addition of the version classifiers.



## [1.1.1] - 15.03.2026

### Changed
- Add the try...except that was removed in dev

## [1.1.0] - 15.03.2026

### Added
- Add `album_artist` to metadata, extracted from the youtubemusicapi album information
- Add information on how to update with pip when update is available.
- Add optional feature to download 
- Add several new metadata settings in the config file `album_artist`, `multiple_artists`, `artist_seperator`, `ffmpeg_metadata` and `cover_art_file`

### Changed
- Make keeping the ffmpeg generated metadata opt-in
- Change m4a tag isrc to ISRC
- MusicBrainz now finds the genre for even more songs, as the data is now fetched by album artist instead of the primary artist IF the album artist is in the songs primary artist. This avoids not finding a genre for songs that contain multiple artists as the primary artist (mistake in the youtube metadata), while still finding the correct artist for songs that have a different primary artist than the album artist
- Add zero-padding to track_pos in the filename
- Add config `cover_art_file` to download the cover art as a jpeg in the same folder as the downloaded audio file.

### Removed
- Remove old_addMetadata function. It was replaced by a new multi-format tagging system in v1.0.0.


## [1.0.0] - 11.03.2026

This is the first major version of SomeDL. Having all the neccessary core fuctionality, this is a great foundation for future features.

In this update the codebase was refactored, a configuration system was added and support for different codecs/formats was added.

### Added
- Dependency: `tomlkit`
- Setting minimum version of `yt-dlp` to `>=2026.3.3`, as there was a important bugfix in that version. https://github.com/yt-dlp/yt-dlp/issues/16118
- User configuration file:
    - Set a download template
    - Set a default download folder
    - Set default output format
    - Set default logging level
    - Option to change ID3v2.x version.
    - And more
- Support for different codecs (m4a/aac, opus, ogg/vorbis, flac) in addition to mp3
- Add `--disable-report` flag to permanently disable download report

### Fixed
- MusicBrainz now returns results, even if the title doesn't completely match ("Hard rock Hallelujah" vs "Hardrock Hallelujah")
- Fix bug where download would fail if yt returns `None` as lyrics instead of valid lyrics or `""`. (Happens with some instrumental-only songs)
- Fix bug where the date would not show up on some music players (Samsung music player), because it was in the ID3v2.4 version.
- Fix incorrect metadata when yt doesn't find the song in the album genius proposed.

### Changed
- Refactoring of codebase, splitting into specific moduels
- Change `--disable-download` flag to `--no-download`
- Show download duration in min and sec when over 60 seconds
- Hide yt-dlp output in INFO log mode (visible via DEBUG)
- Add additional info to download report, including codec/format info
- Sorted cli options into different categories

### Removed
- Remove musicbrainz album guess function. Its inaccurate, is not used and would just create problems in refactoring. (musicbrainz is still needed for genre and mbid data)


## [0.2.2] - 2026.03.02

### Fixed
- Fix problem with invalid file name characters (?*"/\ etc) on windows, where it would throw an error when one of these characters are present in the file name. With a simple sanitize fuction, these characters are now replaced with underscores _



## [0.2.1] - 2026.02.27
### Changed
- Changed deezer warnings to log.warning and log.error instead of print statements
- Add possibility for musicbrainz to only search by artist name if previous normal search and clean search attempts failed. This usually only leads to results if a song name is spelled differently on youtube music as compared to musicbrainz. 
- Added config option "mb_retry_artist_name_only" for this behaviour. Default = True
- In "Check if artist has already been seen", add a check that if the previous attempt has led to no results, continue (either to a entry with correct metadata, or to the end and search for metadata yourself) (but only if mb_retry_artist_name_only is False!). However, if the previous search failed because of a timeout, search again. 
- Add Search with cleaned song title for deezer if previous attempt fails
- The requirement for checking the album is now only if the album type is single or EP, mathching names is no longer required

### Fixed
- Fix bug where genius would not return any results because of empty api token, now it sends an empty header and it works again
- Fixed deezer logging (only show not found warning when the second try has not gotten any result)


## [0.2.0] - 2026.02.24
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

## [0.1.2] - 2026.02.23
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
