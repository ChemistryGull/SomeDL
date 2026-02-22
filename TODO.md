
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
- Downgrade musicbrainz retry from error to warning. Only fail after all retry attempts should be a error
- Add functionality to not show download report. Possibly make download report only generate when downloading more than one song

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
- FEAT: In the html overview, show how long each song lastet to download
- Add lyrics.ovh as lyrics API if youtube fails

## Low Priority
- Create an option that song names are always cleard of everything within a bracked e.g. "(2020 Remastered)"


## Distant future
- GUI?



# General
## General info:
How to proper changelog - https://keepachangelog.com/en/1.1.0/

## List of songs that create problems
- TEMP FIX "ghost - its a sin" https://www.youtube.com/watch?v=XfMVF-o7g1o (Genius says its in a album, but youtube does not have it in that album. Temporary fix is to download it as a single)
- ??? t.A.T.u. - All The Things She Said (Schrödingers API - Musicbrainz API sometimes returns the wrong artist with no tags. sometimes it returns the correct artist. not much i can do there)


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
