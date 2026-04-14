# Changelog
https://keepachangelog.com/en/1.1.0/

## [1.3.1] - 14.04.2026

### Fixed
- Fix critical bug that prevents people from starting SomeDL when they do not have a config yet.


## [1.3.0] - 12.04.2026

Another large update with many small added features. I could never test each edgecase alone, so please let me know if you find any inconsistencies or bugs!

### Added
- Add sync files feature. It lets you define a quick shortcut to download a list of playlists with their own configuration.
- Add functionality to download all albums from an artist with a channel URL
- Add fetch_album to the config.
- Add `--no-album` flag to override the above config setting
- Add download archive feature. Define a download archive file with `--downlaod archive /path/to/archive.txt` or by changing the `download_archive` config. When such a file is defined, all video IDs will be added into that download archive and will be skipped on any future download attempts. 
- Add `--redownload` flag to download a song even if its either in a download archive or the file is already present. If the File is present, it will be overwritten.
- Add `check_if_file_exists` config and corresponding `--skip-file-check` flag to skip checking if a file does already exist. Useful for when you want to have duplicates of the same songs as single & album versions (Having files with the same artist and song title is elsewise not possible, even if in another album)
- Add `somedl update-metadata` functionality. So far it only supports updating or adding lyrics.

### Changed
- In thread_fetch_metadata, switch from iterating over a list to a queue design, to make continous updates via the web-ui possible
- Move header printing into console.print_header() to clean up main function
- Clean and remove unused imports in main
- Move process_song_list_concurrent to processor module to make it reusable for webui
- Entering `somedl download "..."` now does not try to look up a song called "download". 

### Fixed
- Fix bug where setting lyrics_type to "none" would still look up lyrics.
- Add .strip() to all song titles for the (very) rare case that youtube mistakingly adds whitespaces at the end of the title.

### Removed
- Remove unused deprecated process_song_list_sequential function


## [1.2.4] - 09.24.2026

### Fixed
- Fix typos


## [1.2.3] - 31.03.2026

### Fixed
- Fixed issue where it would always download .lrc file, even if `lrc_file` is set `false`


## [1.2.2] - 31.03.2026

### Fixed
- Fixed missing import of console module in genius.py


## [1.2.1] - 31.03.2026

### Fixed
- Fixed bug in the version check cache that would wrongly alert about an update.

## [1.2.0] - 31.03.2026

### Overview
SomeDL 1.2.0 contains big changes to the entire codebase. The core metadata fetching process has been refactored to enable concurrent downloading. These changes also enable more modular reuse of certain parts of the code, allowing the implementation of new features without duplicating much code. Speaking of new features, this update includes a feature to download entrie albums of every input query with the `--fetch-album` flag, a utility to update your existing folder structure with `somedl new-metadata`, and a utitity to import songs aquired by other means, or to update metadata in your existing library with `somedl import`. This update also includes a complete UI rewrite, which was necessary for concurrent downloads. The new UI should be more user-friendy by hiding unnecessary information. Users that still want to see what is going on behind the scenes can change their logging level with the new flags `-v` (just minor warnings, like missing metadata), `-vv` (About the same amout of info as with the old default UI) and `-vvv` (Everything, including debug information).

For feedback - positive and negative - regarding these chagnes, please use the discussion tab or open a new issue!


### Added
- Add already_downloaded_list to download report
- Add `--fetch-album` functionality
- Add lrclib as main lyrics source, youtube is fallback
- Add synced lyrics support (with lrclib as source)
- Add concurrent downloading functionality with user-editable download workers and queue size.
- Add completly new CLI UI which is more user-friendly.
- Add different verbosity flags: `-v`, `-vv` and `-vvv`
- Add `somedl import`: Import songs downloaded with yt-dlp or aquired from other sources into a set folder structure, while also updating the metadata. 
- Add `somedl new-template`: Utility to automatically move your library into a new storeage template.

### Changed
- Refactor album check to metadata_album_check() function
- Reworked the download report
- Implement new clean_song_title function in utils
- Change genius input to song_title_clean over song_title
- Completely changed logging system to Python Rich based console printing.
- Switched to Syslog inspired log servity levels (0-7).
- The version check is only done once per 24 hours, the last check including version is added into somedl_version_cache.json in the SomeDL directory

### Fixed
- Fix filename recognition for files with square brackets in them
- Include check for genius metadata
- Some minor tweaks that hopefully will improve the experience. 

### Removed
- Python Logging based logging. Will completely remove module in the future.

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
