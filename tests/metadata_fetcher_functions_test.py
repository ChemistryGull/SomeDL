import pytest

from unittest.mock import patch, MagicMock

from SomeDL.core.metadata_helper import incr, metadata_album_check, metadata_get_genre_mbid


mock_config = {
    "api": {
        "deezer": True,
        "genius": True,
        "genius_album_check": True,
        "genius_token": "",
        "genius_use_official": False,
        "max_retry": 3,
        "mb_retry_artist_name_only": False,
        "musicbrainz": True
    },
    "download": {
        "always_search_by_query": False,
        "check_if_file_exists": True,
        "cookies_from_browser": "",
        "cookies_path": "",
        "disable_download": False,
        "fetch_albums": False,
        "format": "mp3",
        "id3_version": 3,
        "number_downloaders": 2,
        "output": "{album_artist}/{year} - {album}/{track_pos} - {song}",
        "output_dir": "/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/",
        "prefer_playlist": False,
        "quality": 5,
        "queue_size": 2,
        "strict_url_download": False
    },
    "logging": {
        "config_version": 4,
        "download_report": 2,
        "level": "INFO",
        "log_level": 7
    },
    "metadata": {
        "album_artist": True,
        "artist_separator": "; ",
        "copyright": True,
        "cover_art_file": False,
        "ffmpeg_metadata": False,
        "genre": True,
        "isrc": True,
        "lrc_file": False,
        "lyrics": True,
        "lyrics_fallback_source": "youtube",
        "lyrics_id3_synced_uslt_fallback": False,
        "lyrics_source": "lrclib",
        "lyrics_type": "plain",
        "multiple_artists": False,
        "synced_lyrics_metadata": True
    }
}




def make_yt(album_type="Single", search_results=None, search_artist=None):
    """Creates a fake yt object that returns controlled responses."""
    yt = MagicMock()
    yt.get_album.return_value = {"type": album_type}
    yt.search.return_value = search_results or []
    return yt



YT_PATCH         = "SomeDL.core.metadata_helper.yt"
CONFIG_PATCH     = "SomeDL.core.metadata_helper.config"
GENIUS_PATCH     = "SomeDL.core.metadata_helper.geniusGetAlbumBySongName"
MB_SEARCH_PATCH  = "SomeDL.core.metadata_helper.musicBrainzGetSongByName"
MB_ARTIST_PATCH  = "SomeDL.core.metadata_helper.musicBrainzGetArtistByMBID"


# === Tests ===

class TestTest:
    def test_the_test_test(self):
        assert incr(3) == 4

class TestMetadataAlbumCheck:
    def test_single_changes_album(self):
        """If album type is Single/EP, the album should be updated"""

        mock_input_album = {
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "title": "Just a single",
            "type": "Single",
            "tracks": [
                {"title": "My Song"},
            ]
        }

        mock_yt = MagicMock()
        mock_yt.search.return_value = [{
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "title": "Another album",
            "browseId": "11111"
        }]
        mock_yt.get_album.return_value = {
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "title": "Another album",
            "type": "Album",
            "tracks": [
                {"title": "Track 1"},
                {"title": "My Song"},
            ]
        }


        mock_genius = MagicMock()
        mock_genius.return_value = {
            "album_name": "Another album",
            "artist_name": "My Artist",
            "song_title": "My Song"
        }        

        with patch(YT_PATCH, mock_yt):
            with patch(CONFIG_PATCH, {"api": {"genius": True, "genius_album_check": True}}):
                with patch(GENIUS_PATCH, mock_genius):
                    album_id, album_name, album = metadata_album_check("My Artist", "My Song", "e4a1geav3wer", "My Album", mock_input_album)


        assert album_id == "11111"
        assert album_name == "Another album"
        assert album == mock_yt.get_album.return_value
    
    def test_empty_result_album(self):
        """No change if empty esult"""

        mock_input_album = {
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "title": "Just a single",
            "type": "Single",
            "tracks": [
                {"title": "My Song"},
            ]
        }

        mock_yt = MagicMock()
        mock_yt.search.return_value = ""
        mock_yt.get_album.return_value = {
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "title": "Another album",
            "type": "Album",
            "tracks": [
                {"title": "Track 1"},
                {"title": "My Song"},
            ]
        }


        mock_genius = MagicMock()
        mock_genius.return_value = {
            "album_name": "Another album",
            "artist_name": "My Artist",
            "song_title": "My Song"
        }        

        with patch(YT_PATCH, mock_yt):
            with patch(CONFIG_PATCH, {"api": {"genius": True, "genius_album_check": True}}):
                with patch(GENIUS_PATCH, mock_genius):
                    album_id, album_name, album = metadata_album_check("My Artist", "My Song", "e4a1geav3wer", "My Album", mock_input_album)

        print(album_id)
        assert album_id == "e4a1geav3wer"
        assert album_name == "My Album"
        assert album == mock_input_album


    def test_single_but_track_not_in_yt_album(self):
        """If the original song is not in the tracks of the new album, return the old album"""

        mock_input_album = {
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "type": "Single",
            "tracks": [
                {"title": "My Song"},
            ]
        }

        mock_yt = MagicMock()
        mock_yt.search.return_value = [{
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "title": "Another album",
            "browseId": "11111"
        }]
        mock_yt.get_album.return_value = {
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "title": "Another album",
            "type": "Album",
            "tracks": [
                {"title": "Track 1"},
                {"title": "Other songs..."},
            ]
        }


        mock_genius = MagicMock()
        mock_genius.return_value = {
            "album_name": "Another album",
            "artist_name": "My Artist",
            "song_title": "My Song"
        }        

        with patch(YT_PATCH, mock_yt):
            with patch(CONFIG_PATCH, {"api": {"genius": True, "genius_album_check": True}}):
                with patch(GENIUS_PATCH, mock_genius):
                    album_id, album_name, album = metadata_album_check("My Artist", "My Song", "e4a1geav3wer", "My input Album", mock_input_album)


        assert album_id == "e4a1geav3wer"
        assert album_name == "My input Album"
        assert album == mock_input_album

    def test_single_no_genius_results(self):
        """If the original song is not in the tracks of the new album, return the old album"""

        mock_input_album = {
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "type": "Single",
            "tracks": [
                {"title": "My Song"},
            ]
        }

        mock_yt = MagicMock()
        mock_yt.search.return_value = [{
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "title": "Another album",
            "browseId": "11111"
        }]
        mock_yt.get_album.return_value = {
            "artists": [
                {
                    "name": "My Artist"
                }
            ],
            "title": "Another album",
            "type": "Album",
            "tracks": [
                {"title": "Track 1"},
                {"title": "Other songs..."},
            ]
        }


        mock_genius = MagicMock()
        mock_genius.return_value = {}        

        with patch(YT_PATCH, mock_yt):
            with patch(CONFIG_PATCH, {"api": {"genius": True, "genius_album_check": True}}):
                with patch(GENIUS_PATCH, mock_genius):
                    album_id, album_name, album = metadata_album_check("My Artist", "My Song", "e4a1geav3wer", "My input Album", mock_input_album)


        assert album_id == "e4a1geav3wer"
        assert album_name == "My input Album"
        assert album == mock_input_album


class TestMetadataGetGenreMBID:
    def test_known_metadata(self):
        known_metadata = [
            {
                "artist_name": "Someone",
                "mb_artist_mbid": "eeearr",
                "mb_artist_name": "Someone",
                "mb_genres": "rap",
            },
            {
                "artist_name": "Ghost",
                "mb_artist_mbid": "2bcf2e02-5bc3-4c76-bf76-41126cb11444",
                "mb_artist_name": "Ghost",
                "mb_genres": "heavy metal",
            },
            {
                "artist_name": "Else",
                "mb_artist_mbid": "2baerraer4",
                "mb_artist_name": "Else",
                "mb_genres": "pop",
            },
        ]

        with patch(CONFIG_PATCH, {"api": {"musicbrainz": True}, "metadata": {"genre": True}}):
            result = metadata_get_genre_mbid("Ghost", "Ghost", "Rats", known_metadata)


        assert result["mb_artist_mbid"] == "2bcf2e02-5bc3-4c76-bf76-41126cb11444"
        assert result["mb_artist_name"] == "Ghost"
        assert result["mb_genres"] == "heavy metal"

    def test_get_genre(self):
        known_metadata = [
            {
                "artist_name": "Someone",
                "mb_artist_mbid": "eeearr",
                "mb_artist_name": "Someone",
                "mb_genres": "rap",
            },
            {
                "artist_name": "Ghost",
                "mb_artist_mbid": "2bcf2e02-5bc3-4c76-bf76-41126cb11444",
                "mb_artist_name": "Ghost",
                "mb_genres": "heavy metal",
            },
            {
                "artist_name": "Else",
                "mb_artist_mbid": "2baerraer4",
                "mb_artist_name": "Else",
                "mb_genres": "pop",
            },
        ]

        mock_mb_search = MagicMock()
        mock_mb_search.return_value = {
            "recordings": [
                {
                    "artist-credit": [{
                        "name": "Delain",
                        "artist": {
                            "id": "3b0e8f01-3fd9-4104-9532-1e4b526ce562",
                            "name": "Delain",
                            "sort-name": "Delain",
                            "disambiguation": "Dutch symphonic metal band"
                        }
                    }],
                },
                {
                    "artist-credit": [{
                        "name": "Delain",
                        "artist": {
                            "id": "akjehaougbeig",
                            "name": "Delain",
                            "sort-name": "Delain",
                            "disambiguation": "Dutch symphonic metal band"
                        }
                    }],
                }
            ]
        }

        mock_mb_artist = MagicMock()
        mock_mb_artist.return_value = {
            "name": "Delain",
            "tags": [
                {
                "count": 1,
                "name": "dutch"
                },
                {
                "name": "gothic metal",
                "count": 2
                },
                {
                "name": "metal",
                "count": 1
                },
                {
                "name": "power metal",
                "count": 1
                },
                {
                "count": 10,
                "name": "symphonic metal"
                }
            ]
        }

        with patch(CONFIG_PATCH, {"api": {"musicbrainz": True}, "metadata": {"genre": True}}):
            with patch(MB_SEARCH_PATCH, mock_mb_search):
                with patch(MB_ARTIST_PATCH, mock_mb_artist):
                    with patch("time.sleep", return_value=None):
                        result = metadata_get_genre_mbid("Delain", "Delain", "The Cold", known_metadata)

        assert result["mb_artist_mbid"] == "3b0e8f01-3fd9-4104-9532-1e4b526ce562"
        assert result["mb_artist_name"] == "Delain"
        assert result["mb_genres"] == "symphonic metal"



    def test_get_genre_from_last_iteration(self):
        known_metadata = [
            {
                "artist_name": "Someone",
                "mb_artist_mbid": "eeearr",
                "mb_artist_name": "Someone",
                "mb_genres": "rap",
            },
            {
                "artist_name": "Ghost",
                "mb_failed_timeout": True,
            },
            {
                "artist_name": "The Warning",
            },
            {
                "artist_name": "Else",
                "mb_artist_mbid": "2baerraer4",
                "mb_artist_name": "Else",
                "mb_genres": "pop",
            },
        ]

        mock_mb_search = MagicMock()
        mock_mb_search.return_value = {
            "recordings": [
                {
                    "artist-credit": [{
                        "name": "Delain",
                        "artist": {
                            "id": "3b0e8f01-3fd9-4104-9532-1e4b526ce562",
                            "name": "Delain",
                            "sort-name": "Delain",
                            "disambiguation": "Dutch symphonic metal band"
                        }
                    }],
                },
                {
                    "artist-credit": [{
                        "name": "Delain",
                        "artist": {
                            "id": "akjehaougbeig",
                            "name": "Delain",
                            "sort-name": "Delain",
                            "disambiguation": "Dutch symphonic metal band"
                        }
                    }],
                }
            ]
        }

        mock_mb_artist = MagicMock()
        mock_mb_artist.return_value = {
            "name": "Delain",
            "tags": [
                {
                "count": 1,
                "name": "dutch"
                },
                {
                "name": "gothic metal",
                "count": 2
                },
                {
                "name": "metal",
                "count": 1
                },
                {
                "name": "power metal",
                "count": 1
                },
                {
                "count": 10,
                "name": "symphonic metal"
                }
            ]
        }

        with patch(MB_SEARCH_PATCH, mock_mb_search):
            with patch(MB_ARTIST_PATCH, mock_mb_artist):
                with patch("time.sleep", return_value=None):
                    with patch(CONFIG_PATCH, {"api": {"musicbrainz": True, "mb_retry_artist_name_only": False}, "metadata": {"genre": True}}):
                        result = metadata_get_genre_mbid("Delain", "Delain", "The Cold", known_metadata)
                        new_meta = {"artist_name": "Delain"}
                        new_meta.update(result)
                        known_metadata.append(new_meta)
                        result2 = metadata_get_genre_mbid("Delain", "Delain", "The Cold", known_metadata)

                        result3 = metadata_get_genre_mbid("Ghost", "Ghost", "Rats", known_metadata)
                        
                        result4 = metadata_get_genre_mbid("The Warning", "The Warning", "More", known_metadata)
                    
                    with patch(CONFIG_PATCH, {"api": {"musicbrainz": True, "mb_retry_artist_name_only": False}, "metadata": {"genre": False}}):
                        result5 = metadata_get_genre_mbid("Ghost", "Ghost", "Rats", known_metadata)

        assert result2["mb_artist_mbid"] == "3b0e8f01-3fd9-4104-9532-1e4b526ce562"
        assert result2["mb_artist_name"] == "Delain"
        assert result2["mb_genres"] == "symphonic metal"

        assert result3["mb_artist_mbid"] == "3b0e8f01-3fd9-4104-9532-1e4b526ce562"
        assert result3["mb_artist_name"] == "Delain"
        assert result3["mb_genres"] == "symphonic metal"

        assert result4["mb_artist_mbid"] == ""
        assert result4["mb_artist_name"] == ""
        assert result4["mb_genres"] == ""

        assert result5 == {}