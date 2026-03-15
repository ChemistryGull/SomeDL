# Todo
**This is a messy notes file for me, it is not always up to date**

## Immediate Priority

## High Priority 
- Create this list
- TODO: test with manufactured api results as inputs
- Enable support to keep original audio and not to convert to mp3. This results in a higher quality for less space for most music (e.g. the one in the opus format). Just remux it to a .opus or .ogg (check compatability!!) (*Enable support for other formats like flac*)
- Implement musicbrainz cache
- Easy playlist synchronisation (somedl --sync), with config: sync_targets = [list of playlists]
- Musicbrainz:
    - Now switched to grouping with brackets over strict search with quotes. This should now make all the musicbrainz new searches with musicbrainz obsolete. Observe if this results in more false matches
    - (*switch to 'https://musicbrainz.org/ws/2/artist/?query={artist}&fmt=json', because the current one is not getting the correct results most of the time. also have to rewrite the functions after that because the result will be different*)


### Acutally for next version:
- Show config flag that prints path and config options to the commandline (in json)
- Make a new SUCCESS debug value or sth like that, thats green. should appear if a song has already been downloaded instead of a warning?
- Add a check to checkIfFileExists if {song} and ({aritst} or {album_artist}) are present in template, warn if not.

FOR NEXT VERSION:
- Update config for the new metadata configs
- Check if config is really correct
- Add lrclib support
- add video_id as viable tag


### Docs:
- Not working after update? Install the latest workin version with pip install package_name==version_number.

### UI/UX
- Add information on ~what~ song is downloaded. probably either by adding query or by adding the fetched metadata

## Medium Priority
- Create Flowchart
- Metadata: Add WOAR. Artist website or the streaming websites. MusicBrainz webiste seems to have links, havent found in the api response yet, gotta look
- User configurable id3 version
- FEAT: Give an option to download an entire album (--album flag)
- FEAT: Give an option to download everything from an artist (--artist flag)
- Add lyrics.ovh as lyrics API if youtube fails
- Add functionality to stopp all possible metadata from being added

- Add update metadata functionality. 
    - Example somedl --update -o /path/to/folder --recursive --to-update "Album_artist, genre, ..." --naming-sceme "{artist} - {song} [{sth else...}]"
    - Maybe some warning system, like checking the amount of files
    - some sort of interactive CLI for the update process, where you can select the path, what metadata to change, and the type of search - by yt-dlp video id, a certain output template or by reading youtube urls from the metadata (spotDL adds them into `comment` and SomeDL uses `source` on vorbis & m4a and `WWW Audio Source` on mp3 to store youtube music URLs)
        - This would require the option to toggle every single metadata
        - This would also require to look up which APIs are needed for what info, so skip them if they are not needed (`doMusicBrainz = False or False or True or False`)

## Low Priority
- Create an option that song names are always cleard of everything within a bracked e.g. "(2020 Remastered)"


## Distant future
- GUI?



# General
## General info:
- How to proper changelog - https://keepachangelog.com/en/1.1.0/

- windows vm pw = password

## List of songs that create problems
- TEMP FIX "ghost - its a sin" https://www.youtube.com/watch?v=XfMVF-o7g1o (Genius says its in a album, but youtube does not have it in that album. Temporary fix is to download it as a single)
- ??? t.A.T.u. - All The Things She Said (Schrödingers API - Musicbrainz API sometimes returns the wrong artist with no tags. sometimes it returns the correct artist. not much i can do there)
- NO FIX "Delain - We are the Others" It downlaods the radio version, as this one has way more views for some reason. Querying "Delain - We are the Others Original" downloads the correct one.
- FIXED: "Lordi - Hard rock Haleluja" Youtube is the only service that lists "Hardrock" without a space in between, so Musicbrainz and Deezer do not get results. Possible workaround would be as a fallback only search via artist name. This however may lead to wrong genre data for small artist that are not returned at the top!
- TODO: "LAVINA - Kraj Mene" - MusicBrainz only knows the artist in lowercase.

## General bugs:
This happend once, an youtube proceeded to download the mp4 version instead of the webm. Cannot reproduce. Happens more often now. hope that yt-dlp fixes this soon.
WARNING: [youtube] hlRm3aUzl74: Some android_vr client https formats have been skipped as they are missing a URL. YouTube may have enabled the SABR-only streaming experiment for the current session. See  https://github.com/yt-dlp/yt-dlp/issues/12482  for more details



## Types of URLS
- SUPPORTED     YT-music              https://music.youtube.com/watch?v=MdqaAXrcBv4
- SUPPORTED     YT                    https://www.youtube.com/watch?v=I0WzT0OJ-E0
- SUPPORTED     YT-Shortened          https://youtu.be/I0WzT0OJ-E0?si=miZyWqXVH_IgjkHL
- SUPPORTED     YT-Music-Shortened    Same as yt-music
- SUPPORTED     Playlist              https://www.youtube.com/watch?v=D44vQCTY4Qw&list=RDGMEM_v2KDBP3d4f8uT-ilrs8fQ

## Video types
- MUSIC_VIDEO_TYPE_OMV: Original Music Video - uploaded by original artist with actual video content
- MUSIC_VIDEO_TYPE_UGC: User Generated Content - uploaded by regular YouTube user
- MUSIC_VIDEO_TYPE_ATV: High quality song uploaded by original artist with cover image
- MUSIC_VIDEO_TYPE_OFFICIAL_SOURCE_MUSIC: Official video content, but not for a single track. not seen yet

# List of relevant APIs i found
## Lyrics
- The yt api itself: Free | No auth | Has most lyrics, but no genre info
- Musixmatch: Paid only
- lyrics.ovh: Free | No auth | Only lyrics

# Misc:
#downloadAlbumArt("https://lh3.googleusercontent.com/QTZ68wH7z9K_jOxagJVEgHTG5N9xyb2YMfVITqiceixstw5tXQS6gZHPhZ8-9nUr6OfHOE-bI9Sy0pE=w544-h544-l90-rj")

#getSong("Sabaton - Defence of Moscow")
#getSong("Nirvana smells like teen spirit")
#getSong("Castle rat - wizzard") # It only gets the single version for this one, not the one in the album. The one in the album is a music video anyways, which is bad.
#getSong("In flames trigger") # wrong genre
#getSong("Delain - Moth to a flame") # It only gets the single version for this one too
#getSong("Green day - American idiot") # FIXED: checks on yt if type is album first. Genius makes an "American Idiot (20th Anniversary Deluxe Edition)" out of it sadly. BC of that, deezer does not find anything.
#getSong("Delain invictus")
#getSong("Mushroomhead - Empty Spaces")
#getSong(url="https://music.youtube.com/watch?v=Bsh5NuCI-pM")

#getSong(url="https://www.youtube.com/watch?v=bx9AUS4Titw") # --- Example of non-yt-music song video of type MUSIC_VIDEO_TYPE_OMV. Exceptions have to be made to avoid errors.
#getSong(url="https://www.youtube.com/watch?v=Kyfv-_qMi5Y") # --- Example of normal yt video of type MUSIC_VIDEO_TYPE_UGC. Exceptions have to be made to avoid errors.
#getSong(url="https://www.youtube.com/watch?v=S7LJcjjq6kQ&list=PLZtI2cMRFDYPmT-kL4R-5zf-zL92b2Un_&index=2")
#getSong("TBS - Ü30") # --- Investigate: Genius album guess does not work for this one

#getSong(url="https://music.youtube.com/watch?v=6ZQiyztHzdc")
#getSong("Delain invictus", known_metadata=[dummy_metadata])
#getSong("Delain - Moth to a Flame")



## Howto install on windows
### General python installation:
- Download the installer from the website
- Say yes to everything in the installer
- Install via py -m pip install somedl
- If somedl command is not recognized, add scripts folder to path (This is not a somedl problem, this is a general python issue)
    - Typically something like C:\Users\YourName\AppData\Local\Programs\Python\pythoncore-3.14-64\Scripts depending on your python version and mode of installation
    - Type environment variables in the search, open "Edit the system environment variables"
    - In there, at the bottom click "Environment Variables..."
    - Click on "Path" and then "Edit"
    - Click "New" and then paste the path of the scripts folder in there
    - Click OK on all windows

### Install ffmepeg

https://ffmpeg.org/download.html
https://github.com/BtbN/FFmpeg-Builds/releases

- extract to C:/ffmpeg or somewhere similar
- Go into the extracted folder, there into the bin folder
- there should be a ffmpeg.exe among others.
- Copy the filepath of the bin folder and add it to path (like with python before)

### Install deno
yt-dlp needs deno to properly work (https://github.com/yt-dlp/yt-dlp/wiki/EJS). SomeDL should work without it, but yt-dlp will always print a warning. 
- To install deno, go to https://docs.deno.com/runtime/getting_started/installation/
- If you have npm installed, you can use npm to install deno. If not, open PowerShell (not CMD!) and execute the command provided. (This downloads and installs a script, be aware to only do this from trusted sources!)



## Info on PyPI Upload
- In the account settings on the PyPI website, scroll down and "Add API token"
- Add a file in $HOME/.pypirc and add:
[pypi]
  username = __token__
  password = THE_API_TOKEN
- twine upload dist/*

## Example output:
{
    "album_art": [
        {
            "height": 60,
            "url": "https://lh3.googleusercontent.com/88ec6x-M06m7aiK7hncDUSUO5ogyoB8BcvsjrIs8yO2mMEqzu2hBiP430E5vmn4S-DbEvJ9wm7_CMTjm=w60-h60-l90-rj",
            "width": 60
        },
        {
            "height": 120,
            "url": "https://lh3.googleusercontent.com/88ec6x-M06m7aiK7hncDUSUO5ogyoB8BcvsjrIs8yO2mMEqzu2hBiP430E5vmn4S-DbEvJ9wm7_CMTjm=w120-h120-l90-rj",
            "width": 120
        },
        {
            "height": 226,
            "url": "https://lh3.googleusercontent.com/88ec6x-M06m7aiK7hncDUSUO5ogyoB8BcvsjrIs8yO2mMEqzu2hBiP430E5vmn4S-DbEvJ9wm7_CMTjm=w226-h226-l90-rj",
            "width": 226
        },
        {
            "height": 544,
            "url": "https://lh3.googleusercontent.com/88ec6x-M06m7aiK7hncDUSUO5ogyoB8BcvsjrIs8yO2mMEqzu2hBiP430E5vmn4S-DbEvJ9wm7_CMTjm=w544-h544-l90-rj",
            "width": 544
        }
    ],
    "album_id": "MPREb_TfTrJqjyEdX",
    "album_name": "Excalibur - Remastered 2006 ((Remastered 2006))",
    "artist_all_names": [
        "Grave Digger"
    ],
    "artist_id": "UCo8IuNkx9PS8MswirsKtZpQ",
    "artist_name": "Grave Digger",
    "date": "2006",
    "deezer_album_id": 1221637,
    "deezer_album_label": "Gun",
    "deezer_album_name": "Excalibur - Remastered 2006 (Remastered 2006)",
    "deezer_artist_name": "Grave Digger",
    "deezer_genres": [
        "Rock"
    ],
    "deezer_isrc": "DEC760600301",
    "lyrics": {
        "hasTimestamps": false,
        "lyrics": "Unknown heir\nOrphaned page\nA King to be\nCome his Age\nFor God's sake\n\nSorcerer\nSword in Stone\nRelease will\nBring the Throne\nFor the Chosen One\n\nThe Almighty will point out\nThe only royal blood in the crowd\n\nExcalibur\nSword of the kings\nTake me on your wings\nBack where I belong\nExcalibur\n\nUnworthy\nBound to fail\nNoble Heart\nBound to gain\nChallenge your faith!\n\nSorcerer\nSword in Stone\nRelease it\nAscend the Throne and\nTake the crown\n\nThe Almighty now throws the dice\nArthur the man without a vice\n\nPrecious Sword\nArthur's hand\nHe deserves\nTo rule the land\nLead Britannia\n\nExcalibur lights up the sky\nHard times have been passing by",
        "source": null
    },
    "original_type": "MUSIC_VIDEO_TYPE_ATV",
    "query": null,
    "song_id": "4Ge7OBKLMSo",
    "song_title": "Excalibur (Remastered Version)",
    "song_title_clean": "Excalibur",
    "track_count": 12,
    "track_pos": 3,
    "track_pos_counted": 3,
    "type": "Album",
    "video_type": "MUSIC_VIDEO_TYPE_ATV",
    "yt_url": "https://music.youtube.com/watch?v=4Ge7OBKLMSo"
},


## Typical yt music api request result
{
    "album": {
        "id": "MPREb_TfTrJqjyEdX",
        "name": "Excalibur - Remastered 2006 ((Remastered 2006))"
    },
    "artists": [
        {
            "id": "UCo8IuNkx9PS8MswirsKtZpQ",
            "name": "Grave Digger"
        }
    ],
    "duration": "4:46",
    "duration_seconds": 286,
    "inLibrary": false,
    "isAvailable": true,
    "isExplicit": false,
    "likeStatus": "INDIFFERENT",
    "pinnedToListenAgain": false,
    "thumbnails": [
        {
            "height": 60,
            "url": "https://lh3.googleusercontent.com/88ec6x-M06m7aiK7hncDUSUO5ogyoB8BcvsjrIs8yO2mMEqzu2hBiP430E5vmn4S-DbEvJ9wm7_CMTjm=w60-h60-l90-rj",
            "width": 60
        },
        {
            "height": 120,
            "url": "https://lh3.googleusercontent.com/88ec6x-M06m7aiK7hncDUSUO5ogyoB8BcvsjrIs8yO2mMEqzu2hBiP430E5vmn4S-DbEvJ9wm7_CMTjm=w120-h120-l90-rj",
            "width": 120
        }
    ],
    "title": "Excalibur (Remastered Version)",
    "videoId": "4Ge7OBKLMSo",
    "videoType": "MUSIC_VIDEO_TYPE_ATV",
    "views": null
},
