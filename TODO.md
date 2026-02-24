
# Todo
## Next to do
- Clean up logging, make verbose flag, add verbosity levels

## Immediate Priority

## High Priority 
- Inside album guess the album name gets inevitably overwritten!!!!!!!! Even if the song is not found in the album by youtube!!! This must be fixed, if yt does not find it, either leaf the track number blank but use the albums art and name, OR treat it as a single. NOT BOTH
- Create this list
- TEST: TEST If explicit videos get downloaded. maybe also thest on a VM/on laptop
- BUG: if a search would ever not return a album, or an empty album, the program will crash. prevent that if possible
- TODO: implement song_title_clean for deezer
- BUG: Still have to properly implement failed_list and make try .. except for the whole getSong function in production
- TODO: test with manufactured api results as inputs
- Write a proper readme!!

## Medium Priority
- Create Flowchart
- Implement duration statistic - How long each song takes to download
- Metadata: Add Album Artist
- Metadata: Add Encoding stuff maybe
- Metadata: Add WOAR. Artist website or the streaming websites. MusicBrainz webiste seems to have links, havent found in the api response yet, gotta look
- User configurable id3 version
- Enable support for shortened Youtube links like https://youtu.be/R7o_-8RSrPA?si=q-vq29lIVhjoTnMc
- FEAT: Give an option to download an entire album (--album flag)
- FEAT: Give an option to download everything from an artist (--artist flag)
- Add lyrics.ovh as lyrics API if youtube fails

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
- TODO: "Lordi - Hard rock Haleluja" Youtube is the only service that lists "Hardrock" without a space in between, so Musicbrainz and Deezer do not get results. Possible workaround would be as a fallback only search via artist name. This however may lead to wrong genre data for small artist that are not returned at the top!


## Types of URLS
- SUPPORTET     YT-music              https://music.youtube.com/watch?v=MdqaAXrcBv4
- SUPPORTET     YT                    https://www.youtube.com/watch?v=I0WzT0OJ-E0
- SUPPORTET     YT-Shortened          https://youtu.be/I0WzT0OJ-E0?si=miZyWqXVH_IgjkHL
- SUPPORTET     YT-Music-Shortened    Same as yt-music
- SUPPORTET     Playlist              https://www.youtube.com/watch?v=D44vQCTY4Qw&list=RDGMEM_v2KDBP3d4f8uT-ilrs8fQ

## Video types
- MUSIC_VIDEO_TYPE_OMV: Original Music Video - uploaded by original artist with actual video content
- MUSIC_VIDEO_TYPE_UGC: User Generated Content - uploaded by regular YouTube user
- MUSIC_VIDEO_TYPE_ATV: High quality song uploaded by original artist with cover image
- MUSIC_VIDEO_TYPE_OFFICIAL_SOURCE_MUSIC: Official video content, but not for a single track. not seen yet



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
