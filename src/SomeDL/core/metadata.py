import json
import base64
import re
from pathlib import Path
#from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, ID3NoHeaderError
#import mutagen
import  mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, USLT, WOAS, WOAR, APIC, TYER, TDRC, SYLT
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4, MP4Cover, MP4FreeForm, AtomDataType
from mutagen.flac import FLAC, Picture
from mutagen import File

from SomeDL.utils.logging import log, printj
from SomeDL.utils.config import config
from SomeDL.api.web_requests import downloadAlbumArt



EasyID3.RegisterTextKey('comment', 'COMM')
EasyID3.RegisterTextKey('audio_source', 'WOAS')


# def addMetadata(metadata: str, mp3_file: str):
def addMetadata(metadata, path):

    if not len(metadata.get("album_art", [])) == 0:
        album_art_url = metadata.get("album_art", [{}])[-1].get("url")
        log.debug(f'Album art size: {metadata.get("album_art", [{}])[-1].get("height")} x {metadata.get("album_art", [{}])[-1].get("width")}')
    else:
        album_art_url = None
    
    if album_art_url:
        log.debug("Downloading Album Artwork...")
        album_art_data = downloadAlbumArt(album_art_url)
    else: 
        album_art_data = None


    # === Download cover art as .jpg if wanted ===
    if config["metadata"]["cover_art_file"] and album_art_data:
        jpg_path = Path(path).parent / "cover.jpg"
        if not jpg_path.exists():
            with open(jpg_path, "wb") as f:
                f.write(album_art_data)


    try:
        audio = File(path, easy=False)
        if audio is None:
            # Format not recognised at all
            log.error(f'File "{path}" is not a in valid format')
            return False
        audio_type = audio.__class__.__name__.lower()
    except Exception as e:
        # Truncated files, permission errors, etc.
        log.error(f'Could not add metadata')
        return False


    log.debug(f'Audio type: {audio_type}')

    match audio_type:
        case "oggopus" | "oggvorbis":
            tag_vorbis(audio, path, metadata)

            if album_art_data:
                picture = Picture()
                picture.data = album_art_data
                picture.type = 3
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                encoded = base64.b64encode(picture.write()).decode("ascii")
                audio["metadata_block_picture"] = [encoded]

            audio.save()

        case "flac":
            tag_vorbis(audio, path, metadata)

            if album_art_data:
                picture = Picture()
                picture.data = album_art_data
                picture.type = 3
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                audio.clear_pictures()
                audio.add_picture(picture)

            audio.save()

        case "mp4":
            tag_m4a(audio, path, metadata, album_art_data)

        case "mp3":
            tag_mp3(path, metadata, album_art_data)

            

        case _:
            log.error(f'Audio type "{audio_type}" is not supported. Proceeding without adding metadata')




def tag_mp3(path, metadata, album_art_data):

    try:
        tag = EasyID3(path)
    except:
        tag = mutagen.File(path, easy=True)
        tag.add_tags()
        log.debug("EasyID3 adding new tags")

    if not config["metadata"]["ffmpeg_metadata"]:
        tag.delete()

    if config["metadata"]["multiple_artists"]:
        tag['artist'] = config["metadata"]["artist_separator"].join(metadata.get("artist_all_names", ""))
    else:
        tag['artist'] = metadata.get("artist_name", "")
    
    tag['title'] = metadata.get("song_title", "")
    # tag['date'] = metadata.get("date", "") # --- will be added directly according to the version
    tag['album'] = metadata.get("album_name", "")
    tag['genre'] = metadata.get("mb_genres", "")


    track_pos = metadata.get("track_pos")
    track_count = metadata.get("track_count")

    if track_pos:
        if track_count:
            tag["tracknumber"] = f'{track_pos}/{track_count}'
        else:
            tag["tracknumber"] = str(track_pos)

    if metadata.get("album_artist") and config["metadata"]["album_artist"]:
        tag['albumartist'] = metadata.get("album_artist", "")

    #tag['discnumber'] = 'mydiscnumber'
    # tag['audio_source'] = f'https://music.youtube.com/watch?v={metadata.get("song_id", "")}'
    # tag['comment'] = f'https://music.youtube.com/watch?v={metadata.get("song_id", "")}'

    if metadata.get("mb_artist_mbid", ""):
        tag['musicbrainz_artistid'] =  metadata.get("mb_artist_mbid", "")
    
    if metadata.get("deezer_isrc", "") and config["metadata"]["isrc"]:
        tag['isrc'] =  metadata.get("deezer_isrc", "")

    if metadata.get("date") and metadata.get("deezer_album_label") and config["metadata"]["copyright"]:
        tag['copyright'] =  f'{metadata.get("date", "")} {metadata.get("deezer_album_label", "")}'
    else:
        log.debug("Adding no copyright info to metadata as some info is missing")

    tag.save(v2_version=config["download"]["id3_version"])

    #TODO: WOAR = https://www.artistwebsite.com ...oder... WOAR = https://musicbrainz.org/artist/<MBID>
    #TODO: genre: add multiple genres. Seperated by a / on v2.3 (tho not exactly supportet i guess) or a \0 on v2.4. Just a guess to


    # Source: https://stackoverflow.com/questions/42231932/writing-id3-tags-using-easyid3



    id3 = ID3(path)
    id3.delall("USLT")
    id3.delall("WOAS")
    id3.delall("WOAR")
    id3.delall("APIC")


    
    if config["download"]["id3_version"] == 4:
        # --- Add TDRC (recording time) v2.4
        id3.add(TDRC(encoding=3, text=metadata.get("date", "")))
    else:
        # --- Add TYER (year only) v2.3
        id3.add(TYER(encoding=3, text=metadata.get("date", "")))


    if metadata.get("lyrics") and config["metadata"]["lyrics"]:
        id3.add(USLT(
            encoding=3,
            lang = "XXX",
            desc = "",
            text = metadata.get("lyrics", {}).get("lyrics", "")
        ))

    # if metadata.get("synced_lyrics"):
    #     id3.add(SYLT(
    #         encoding=3,
    #         lang = "XXX",
    #         desc = "",
    #         text = conv_lrc_to_sylt(metadata.get("synced_lyrics", ""))
    #     ))
    
    id3.add(WOAS(
        url=f'https://music.youtube.com/watch?v={metadata.get("song_id", "")}'
    ))
    # TODO: Add urls to the artist website or the streaming websites. Multiple WOAR tags can be added (appear as "website" on kid3)
    # id3.add(WOAR(
    #     encoding=3,
    #     url='https://music.youtube.com/watch?v=text',
    #     content="xxx"
    # ))

    if album_art_data:
        id3.add(APIC(
            encoding=1,  # (Same as spotdl)
            mime='image/jpeg',  # or 'image/png' depending on the image type
            type=3,  # Cover (front); (same as spotld)
            desc='Cover',
            data=album_art_data
        ))

    id3.save(v2_version=3)


def conv_lrc_to_sylt(synced_lyrics):
    synced = []
    plain_lines = []


    for line in synced_lyrics.split("\n"):
        print(line)
        m = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\](.*)").match(line.strip())
        if not m:
            continue

        minutes = int(m.group(1))
        seconds = float(m.group(2))
        text = m.group(3).strip()

        ms = int((minutes * 60 + seconds) * 1000)

        synced.append((text, ms))
        plain_lines.append(text)

    print(" -- -- -- ")
    print(synced)
    # print(plain_lines)
    return synced


def tag_vorbis(audio, path, metadata):
    if not config["metadata"]["ffmpeg_metadata"]:
        audio.delete()

    if config["metadata"]["multiple_artists"]:
        audio["artist"]   = metadata.get("artist_all_names", "")
    else:
        audio["artist"]   = [metadata.get("artist_name", "")]
    
    audio["title"]        = [metadata.get("song_title", "")]
    audio["date"]         = [metadata.get("date", "")]
    audio["album"]        = [metadata.get("album_name", "")]
    audio["genre"]        = [metadata.get("mb_genres", "")]
    audio['tracknumber']  = str(metadata.get("track_pos", ""))
    audio['tracktotal']   = str(metadata.get("track_count", ""))

    if metadata.get("album_artist") and config["metadata"]["album_artist"]:
        audio["albumartist"] = metadata.get("album_artist", "")

    if metadata.get("mb_artist_mbid", ""):
        audio['musicbrainz_artistid'] = [metadata.get("mb_artist_mbid", "")]
    
    if metadata.get("deezer_isrc", "") and config["metadata"]["isrc"]:
        audio['isrc'] = [metadata.get("deezer_isrc", "")]

    if metadata.get("date") and metadata.get("deezer_album_label") and config["metadata"]["copyright"]:
        audio['copyright'] = [f'{metadata.get("date", "")} {metadata.get("deezer_album_label", "")}']
    else:
        log.debug("Adding no copyright info to metadata as some info is missing")

    audio['source'] = [f'https://music.youtube.com/watch?v={metadata.get("song_id", "")}']

    if metadata.get("lyrics") and config["metadata"]["lyrics"]:
        audio['lyrics'] = [metadata.get("lyrics", {}).get("lyrics", "")]


    
    # audio["comment"]      = "Some comment"
    # audio["composer"]     = "Composer Name"
    # audio["discnumber"]   = "1" 


def tag_m4a(audio, path, metadata, album_art_data):
    if not config["metadata"]["ffmpeg_metadata"]:
        audio.delete()

    # Source: https://mutagen.readthedocs.io/en/latest/api/mp4.html#mutagen.mp4.MP4Tags

    if config["metadata"]["multiple_artists"]:
        audio["\xa9ART"] = [config["metadata"]["artist_separator"].join(metadata.get("artist_all_names", ""))]   
    else:
        audio["\xa9ART"] = [metadata.get("artist_name", "")]        # artist

    audio["\xa9nam"] = [metadata.get("song_title", "")]         # title
    audio["\xa9day"] = [metadata.get("date", "")]               # date
    audio["\xa9alb"] = [metadata.get("album_name", "")]         # album
    audio["\xa9gen"] = [metadata.get("mb_genres", "")]          # genre

    # --- Track number and total as tuple in a list
    track_pos   = metadata.get("track_pos", 0)
    track_count = metadata.get("track_count", 0)
    audio["trkn"] = [(int(track_pos) if track_pos else 0, int(track_count) if track_count else 0)]


    if metadata.get("album_artist") and config["metadata"]["album_artist"]:
        audio["aART"] = metadata.get("album_artist", "")

    if metadata.get("mb_artist_mbid", ""):
        audio[f"----:com.apple.iTunes:musicbrainz_artistid"] = [MP4FreeForm(metadata.get("mb_artist_mbid", "").encode("utf-8"), AtomDataType.UTF8)]
    
    if metadata.get("deezer_isrc", "") and config["metadata"]["isrc"]:
        audio[f"----:com.apple.iTunes:ISRC"] = [MP4FreeForm(metadata.get("deezer_isrc", "").encode("utf-8"), AtomDataType.UTF8)]

    if metadata.get("date") and metadata.get("deezer_album_label") and config["metadata"]["copyright"]:
        audio['cprt'] = [f'{metadata.get("date", "")} {metadata.get("deezer_album_label", "")}']
    else:
        log.debug("Adding no copyright info to metadata as some info is missing")



    source = f'https://music.youtube.com/watch?v={metadata.get("song_id", "")}'
    audio[f"----:com.apple.iTunes:source"] = [MP4FreeForm(source.encode("utf-8"), AtomDataType.UTF8)]

    if metadata.get("lyrics") and config["metadata"]["lyrics"]:
        audio["\xa9lyr"] = metadata.get("lyrics", {}).get("lyrics", "")

    # audio["aART"]    = ["Album Artist"]                          # album artist
    # audio["\xa9cmt"] = ["Some comment"]                         # comment

    if album_art_data:
        audio["covr"] = [MP4Cover(album_art_data, imageformat=MP4Cover.FORMAT_JPEG)]

    audio.save()



dummy_metadata = {
    "album_art": [
        {
            "height": 60,
            "url": "https://lh3.googleusercontent.com/QTZ68wH7z9K_jOxagJVEgHTG5N9xyb2YMfVITqiceixstw5tXQS6gZHPhZ8-9nUr6OfHOE-bI9Sy0pE=w60-h60-l90-rj",
            "width": 60
        },
        {
            "height": 120,
            "url": "https://lh3.googleusercontent.com/QTZ68wH7z9K_jOxagJVEgHTG5N9xyb2YMfVITqiceixstw5tXQS6gZHPhZ8-9nUr6OfHOE-bI9Sy0pE=w120-h120-l90-rj",
            "width": 120
        },
        {
            "height": 226,
            "url": "https://lh3.googleusercontent.com/QTZ68wH7z9K_jOxagJVEgHTG5N9xyb2YMfVITqiceixstw5tXQS6gZHPhZ8-9nUr6OfHOE-bI9Sy0pE=w226-h226-l90-rj",
            "width": 226
        },
        {
            "height": 544,
            # "url": "https://lh3.googleusercontent.com/QTZ68wH7z9K_jOxagJVEgHTG5N9xyb2YMfVITqiceixstw5tXQS6gZHPhZ8-9nUr6OfHOE-bI9Sy0pE=w544-h544-l90-rj",
            "url": "https://lh3.googleusercontent.com/CeUT3fMuN6gZrTQCb9N5BTGs51QkQyJB1M2V19hIEUZleLsf-Xm0RdybqyCYOMxRKBJtd1xtTX1Y-qtz=w544-h544-l90-rj",
            "width": 544
        }
    ],
    "album_id": "MPREb_B9YcEZY20ip",
    "album_name": "Dark Waters",
    "artist_all_names": [
        "Delain"
    ],
    "artist_id": "UCPIXyGsEUrGIz7olJ1d7-Ig",
    "artist_name": "Delain",
    "date": "2023",
    "deezer_album_id": 371540297,
    "deezer_album_label": "Napalm Records Handels GmbH",
    "deezer_album_name": "Dark Waters",
    "deezer_artist_name": "Delain",
    "deezer_genres": [
        "Heavy Metal"
    ],
    "deezer_isrc": "ATN262214104",
    "lyrics": {
        "hasTimestamps": False,
        "lyrics": "Deceitful cries under the sun\nTo crucify\nWhat have you done?\nI will not fight your shameful war\nOr spread more lies\nBut I must stand my ground\n\nInvictus I remain\n\nYou're heading towards your own destruction\nYou're heading towards your own destruction\n\nBut what is gained (You mutineers)\nBy a war of pride and greed? (You've made a scene)\nDebris of your failed siege (Now face your empty new frontier - justice)\nWhat you're fighting for you've made a field (You should have learned your end is near)\nOf embers and barbarity (Do you feel it?)\n\nAnd what remains (You mutineers)\nIn the wake of enmity? (You've made a scene)\nDestruction six feet deep (Now face your empty new frontier - justice)\nYou can never take what I've achieved (You should have learned your end is near)\nNev\u0435r, you'll be buried a namel\u0435ss thief (Do you feel it burn?)\n\nWe are now the cruel collective faction\nBow down or face destruction\n\nAnd what remains (You mutineers)\nIn the wake of enmity? (You've made a scene)\nDestruction six feet deep (Now face your empty new frontier - justice)\nYou can never take what I've achieved (You should have learned your end is near)\nNev\u0435r, you'll be buried a namel\u0435ss thief (Do you feel it burn?)\n\nI'm gonna watch your fire burn your eyes\nI'm gonna stand in truth you can't deny\nYou crowned a fool\nNow bear your shame\nI will not condescend\nTo bow before your claim\nNot this time\nThis is your last goodbye\n\nBearing the wounds you've given me\nKnowing they're worth the victory\nHolding, always standing my ground\nGround\nLosing your pride and dignity\nScreaming your rage and treachery\nWaging this war of misery now\nNow\n\nInvictus maneo\nPerge ad victoriam\nUndaunted, in the end\nI'll be standing no more sorrow\nI'm watching far below\nSoaring pride is your downfall\nYour cunning collective\nFierce today but gone tomorrow\n\nInvictus maneo\nPerge ad victoriam\nUndaunted, in the end\nI'll be standing no more sorrow\nI'm watching far below\nSoaring pride is your downfall\nYour cunning collective\nFierce today but gone tomorrow",
        "source": None
    },
    "mb_artist_mbid": "3b0e8f01-3fd9-4104-9532-1e4b526ce562",
    "mb_artist_name": "Delain",
    "mb_genres": "symphonic metal",
    "query": "Delain invictus",
    "song_id": "3J8VwHPRyN8",
    "song_title": "Invictus (feat. Marco Hietala, Paolo Ribaldini & Marko Hietala)",
    "track_count": 21,
    "track_pos": 9,
    "track_pos_counted": 9,
    "type": "Album",
    "video_type": "MUSIC_VIDEO_TYPE_ATV",
    "yt_url": "https://music.youtube.com/watch?v=3J8VwHPRyN8"
}



#tag_opus("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.opus")
#tag_ogg("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.ogg")
#tag_flac("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.flac")
#tag_m4a("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.m4a")
#tag_mp3("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.mp3")

#addMetadata("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.opus", dummy_metadata)
#addMetadata("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.ogg", dummy_metadata)
#addMetadata("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.flac", dummy_metadata)
#addMetadata("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.m4a", dummy_metadata)
#addMetadata("/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Delain/2020 - Apocalypse & Chill/Creatures.mp3", dummy_metadata)
#addMetadata(dummy_metadata, "/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/Bad Omens - THE DRAIN.m4a")



