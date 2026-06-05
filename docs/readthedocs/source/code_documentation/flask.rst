Flask documentation
===================

All of these endpoints might change at any point in future updates. Please notify me on `GitHub <https://github.com/ChemistryGull/SomeDL>`_ if you find mistakes in this documentation. 

Download & General
------------------

.. http:get:: /status

    Get the current processing status, containing a list of active items, a list of finished items and the number of items in the queue.

    In ``active_items``, the ``text`` element contains the artist name and song title, as well as the download number.
    ``data`` contains a list of processes this item went through in the order shown below, each with a status 
    (``active``, ``success``, ``part_succ``, ``not_found``, ``failed``, ``skipped``, ``hide``, ) 
    and a message showing additional information in an active state, though sometimes formated as a python rich string.

    Because this design is reused from the CLI, its not the most straightforward.

    :statuscode 200: Success
    :statuscode 500: Server error

    :resheader Content-Type: application/json

    :>json dict active_items: Items currently being processed, with the SomeDL ID as key. 
    :>json dict finished_items: Doct of completed items, with the SomeDL ID as key and the status as property.
    :>json int items_in_queue: Number of items waiting in the queue

    **Example request (JavaScript):**

    .. code-block:: javascript

        const res = await fetch("/status");
        const data = await res.json();

    **Example response:**

    .. code-block:: json

        {
            "active_items": {
                "17806688160307190000001":  {
                    "text": "4/0 Delain - Not Enough",
                    "data": {
                        "album": {
                            "message": "Nothing",
                            "status": "success"
                        },
                        "get_lyrics": {
                            "status": "skipped",
                            "message": "Nothing"
                        },
                        "musicbrainz": {
                            "status": "success",
                            "message": "Nothing"
                        },
                        "deezer": {
                            "status": "success",
                            "message": "Nothing"
                        },
                        "wait_queue": {
                            "status": "hide",
                            "message": "Nothing"
                        },
                        "downloading": {
                            "status": "success",
                            "message": "Nothing"
                        },
                        "albumart": {
                            "status": "success",
                            "message": "Nothing"
                        },
                        "addmetadata": {
                            "status": "success",
                            "message": "Nothing"
                        }
                    }
                },
                "17771447553066950000002": {
                    "text": "5/0 The Warning - EVOLVE",
                    "data": {
                        "album": {
                            "status": "success",
                            "message": "Nothing"
                        },
                        "get_lyrics": {
                            "status": "skipped",
                            "message": "Nothing"
                        },
                        "musicbrainz": {
                            "status": "success",
                            "message": "Nothing"
                        },
                        "deezer": {
                            "status": "success",
                            "message": "Nothing"
                        },
                        "wait_queue": {
                            "status": "hide",
                            "message": "Nothing"
                        },
                        "downloading": {
                            "status": "active",
                            "message": "yt-dlp: Postprocessing  (Got 3.29MiB at [green]\u001b[0;32m3.83MiB/s\u001b[0m[/])"
                        }
                    }
                }
            },
            "finished_items": {
                "17806688160307190000001": "success",
                "17806688160354710000001": "success",
                "17806688160397410000001": "success"
            },
            "items_in_queue": 5
        }




.. http:get:: /get-queue

    Get the download queue as well as the active items. Usually used after a page refresh.

    The list ``queue`` contains the items that are currently being processed. The content of each item depends on how the song was requested.
    A download by search query adds the first entry to the queue, a download by URL or from the YouTube Search adds the second entry.
    The only entries that are guaranteed are ``somedl_id`` for all items, ``text_query`` for query search request tiems and ``song_title`` and ``artist_name`` for URL request items.

    :statuscode 200: Success
    :statuscode 500: Server error

    :resheader Content-Type: application/json

    :>json dict active: same as in ``/status`` request. 
    :>json list queue: List of the items in queue.

    **Example response:**

    .. code-block:: json

        {
            "active": {
                "17806688160307332000002": {
                    "data": {},
                    "text": "2/0 Delain - We Are The Others (Radio Version)"
                }
            },
            "queue": [
                {
                    "somedl_id": "17806703611854036000001",
                    "text_query": "delain - the cold",
                    "video_type": "Search query",
                    "video_type_original": "Search query"
                },
                {
                    "album_id": "MPREb_fMsob6AXjNV",
                    "album_name": "Ego",
                    "artist_all_names": [
                        "The Warning"
                    ],
                    "artist_id": "UCmZbBc8qMj0v9Q6dC-kw4Xg",
                    "artist_name": "The Warning",
                    "lyrics_id": "MPLYt_fMsob6AXjNV-1",
                    "original_url_id": "u-BMzP-RLd4",
                    "somedl_id": "17806707385822792000001",
                    "song_id": "u-BMzP-RLd4",
                    "song_title": "Ego",
                    "song_title_clean": "Ego",
                    "video_type": "MUSIC_VIDEO_TYPE_ATV",
                    "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
                    "yt_url": "https://www.youtube.com/watch?v=u-BMzP-RLd4"
                }
            ]
        }


.. http:post:: /shutdown

    Triggers a shutdown of the SomeDL CLI.

    **Response:**

    :statuscode 200: Shutdown successfully triggered
    :resheader Content-Type: application/json

    **Example response:**

    .. code-block:: json

        {
            "message": "shutdown triggered"
        }




.. http:post:: /add

    Request to download a list of search queries or URLs, similar to the CLI.

    **Request body:**

    .. code-block:: json

        {
            "input_list": ["Artist - Title", "Artist - Title"]
        }

    **Behavior:**

    - Expands input using ``generateSongList()``
    - Adds each song to ``song_list_queue`` for download

    **Responses:**

    :statuscode 200: Items successfully added to queue
    :statuscode 400: Missing or invalid "item" field
    :statuscode 500: Failed to generate song list, internal server error.

    :resheader Content-Type: application/json

    :>json list song_list: List of items to download, same as ``queue`` in ``/get-queue``.


    **Success response (200):**

    .. code-block:: json

        {
            "song_list": [
                {
                    "somedl_id": "17806724760830844000001",
                    "text_query": "delain - not enough",
                    "video_type": "Search query",
                    "video_type_original": "Search query"
                }, 
                {
                    "album_id": "MPREb_B9YcEZY20ip",
                    "album_name": "Dark Waters",
                    "artist_all_names": [
                        "Delain"
                    ],
                    "artist_id": "UCPIXyGsEUrGIz7olJ1d7-Ig",
                    "artist_name": "Delain",
                    "lyrics_id": "MPLYt_B9YcEZY20ip-1",
                    "original_url_id": "WOZOwTG9dmU",
                    "somedl_id": "17806739333906158000001",
                    "song_id": "WOZOwTG9dmU",
                    "song_title": "Hideaway Paradise",
                    "song_title_clean": "Hideaway Paradise",
                    "video_type": "MUSIC_VIDEO_TYPE_ATV",
                    "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
                    "yt_url": "https://www.youtube.com/watch?v=WOZOwTG9dmU"
                }
            ]
        }

    **Error response (400):**

    .. code-block:: json

        {
            "error": "No item"
        }

    **Error response (500):**

    .. code-block:: json

        {
            "error": "Failed to generate song list, internal server error"
        }


.. http:get:: /get-version

    Returns SomeDL version.

    **Response:**

    :statuscode 200: Shutdown successfully triggered
    :resheader Content-Type: application/json

    **Example response:**

    .. code-block:: json

        {
            "v": "1.5.0"
        }


.. http:get:: /get-history

    Returns the download history of the current session.

    **Response:**

    :statuscode 200: Shutdown successfully triggered
    :statuscode 500: Server error
    :resheader Content-Type: application/json

    :>json dict metadata_success_list: List of songs that were successfully downloaded
    :>json dict already_downloaded_list: List of songs that were already downloaded and thus skipped
    :>json int failed_list: List of songs that failed to download

    **Example response:**

    .. code-block:: json

        {
            "metadata_success_list": [
                {
                    "album_art": [
                        {
                            "height": 60,
                            "url": "https://yt3.googleusercontent.com/S0y9a8Dv3SlLbxf0SAAfY4UmgHLHxto-77tyThyl0aQaFKVz8rrruDsdH72j_ibf6qJdGi2yh8r1rDfr=w60-h60-l90-rj",
                            "width": 60
                        },
                        {
                            "height": 120,
                            "url": "https://yt3.googleusercontent.com/S0y9a8Dv3SlLbxf0SAAfY4UmgHLHxto-77tyThyl0aQaFKVz8rrruDsdH72j_ibf6qJdGi2yh8r1rDfr=w120-h120-l90-rj",
                            "width": 120
                        },
                        {
                            "height": 226,
                            "url": "https://yt3.googleusercontent.com/S0y9a8Dv3SlLbxf0SAAfY4UmgHLHxto-77tyThyl0aQaFKVz8rrruDsdH72j_ibf6qJdGi2yh8r1rDfr=w226-h226-l90-rj",
                            "width": 226
                        },
                        {
                            "height": 544,
                            "url": "https://yt3.googleusercontent.com/S0y9a8Dv3SlLbxf0SAAfY4UmgHLHxto-77tyThyl0aQaFKVz8rrruDsdH72j_ibf6qJdGi2yh8r1rDfr=w544-h544-l90-rj",
                            "width": 544
                        }
                    ],
                    "album_artist": "Gojira",
                    "album_id": "MPREb_NXcXGpvbU9K",
                    "album_name": "Magma",
                    "artist_all_names": [
                        "Gojira"
                    ],
                    "artist_id": "UCPdbkw3S_0ZSHAqlnxo9E_g",
                    "artist_name": "Gojira",
                    "date": "2016",
                    "deezer_album_id": 13304751,
                    "deezer_album_label": "Roadrunner Records",
                    "deezer_album_name": "Magma",
                    "deezer_artist_name": "Gojira",
                    "deezer_genres": [
                        "Heavy Metal"
                    ],
                    "deezer_isrc": "NLA321600033",
                    "download_time": 19.918654441833496,
                    "duration": 270,
                    "filetype": "mp3",
                    "label": {
                        "id": "17806746083312502000002",
                        "text": "2/0 Gojira - Stranded"
                    },
                    "mb_artist_mbid": "1c5efd53-d6b6-4d63-9d22-a15025cf5f07",
                    "mb_artist_name": "Gojira",
                    "mb_genres": "progressive metal",
                    "metadata_time": 28.545751810073853,
                    "somedl_id": "17806746083312502000002",
                    "song_id": "zgychWIo6UA",
                    "song_title": "Stranded",
                    "song_title_clean": "Stranded",
                    "text_query": "gojira - stranded",
                    "total_time": "48.5 seconds",
                    "track_count": 10,
                    "track_pos": 4,
                    "track_pos_counted": 4,
                    "type": "Album",
                    "video_type": "MUSIC_VIDEO_TYPE_ATV",
                    "video_type_original": "Search query",
                    "yt_url": "https://music.youtube.com/watch?v=zgychWIo6UA"
                }
            ],
            "already_downloaded_list": [
                {
                    "album_id": "MPREb_iUk3tvhGHje",
                    "album_name": "We Are The Others",
                    "artist_all_names": [
                        "Delain"
                    ],
                    "artist_id": "UCPIXyGsEUrGIz7olJ1d7-Ig",
                    "artist_name": "Delain",
                    "duration": 284,
                    "label": {
                        "id": "17806746083312340000001",
                        "text": "1/0 Delain - Not Enough"
                    },
                    "somedl_id": "17806746083312340000001",
                    "song_id": "oQ5DHtZU3RI",
                    "song_title": "Not Enough",
                    "song_title_clean": "Not Enough",
                    "text_query": "delain not enough",
                    "video_type": "MUSIC_VIDEO_TYPE_ATV",
                    "video_type_original": "Search query",
                    "yt_url": "https://music.youtube.com/watch?v=oQ5DHtZU3RI"
                }
            ],
            "failed_list": [
                {
                    "album_art": [
                        {
                            "height": 60,
                            "url": "https://yt3.googleusercontent.com/7ZsvBXfYxrHSAERxp-OX23Ew52oR9resSqGUaHOuiBf3xUF8YY71gldt_PMm29jtxYG3dw_WwYV9vaU=w60-h60-l90-rj",
                            "width": 60
                        },
                        {
                            "height": 120,
                            "url": "https://yt3.googleusercontent.com/7ZsvBXfYxrHSAERxp-OX23Ew52oR9resSqGUaHOuiBf3xUF8YY71gldt_PMm29jtxYG3dw_WwYV9vaU=w120-h120-l90-rj",
                            "width": 120
                        },
                        {
                            "height": 226,
                            "url": "https://yt3.googleusercontent.com/7ZsvBXfYxrHSAERxp-OX23Ew52oR9resSqGUaHOuiBf3xUF8YY71gldt_PMm29jtxYG3dw_WwYV9vaU=w226-h226-l90-rj",
                            "width": 226
                        },
                        {
                            "height": 544,
                            "url": "https://yt3.googleusercontent.com/7ZsvBXfYxrHSAERxp-OX23Ew52oR9resSqGUaHOuiBf3xUF8YY71gldt_PMm29jtxYG3dw_WwYV9vaU=w544-h544-l90-rj",
                            "width": 544
                        }
                    ],
                    "album_artist": "Hämatom",
                    "album_id": "MPREb_r7FwDjQUQDr",
                    "album_name": "Die Liebe ist tot",
                    "artist_all_names": [
                        "Hämatom"
                    ],
                    "artist_id": "UC2UdnSVg1t2xQAgRbI74ETw",
                    "artist_name": "Hämatom",
                    "date": "2021",
                    "deezer_album_id": 267181942,
                    "deezer_album_label": "Anti Alles",
                    "deezer_album_name": "Die Liebe ist tot",
                    "deezer_artist_name": "Hämatom",
                    "deezer_genres": [
                        "Rock"
                    ],
                    "deezer_isrc": "FRX452148688",
                    "duration": 224,
                    "label": {
                        "id": "17806746083312592000003",
                        "text": "3/0 Hämatom - Liebe auf den ersten xxxx"
                    },
                    "mb_artist_mbid": "f10ad2fb-d81e-4075-9070-453f481b5fc9",
                    "mb_artist_name": "Hämatom",
                    "mb_genres": "neue deutsche härte",
                    "metadata_time": 9.31917667388916,
                    "somedl_id": "17806746083312592000003",
                    "song_id": "G0rQKudItF4",
                    "song_title": "Liebe auf den ersten xxxx",
                    "song_title_clean": "Liebe auf den ersten xxxx",
                    "text_query": "hämatom - liebe auf dem ersten xxxx",
                    "track_count": 10,
                    "track_pos": 4,
                    "track_pos_counted": 4,
                    "type": "Album",
                    "video_type": "MUSIC_VIDEO_TYPE_ATV",
                    "video_type_original": "Search query",
                    "yt_url": "https://music.youtube.com/watch?v=G0rQKudItF4"
                }
            ]
        }



Control
-------

.. http:post:: /pause-download

    Request pausing the download process.

    **Response:**

    :statuscode 200: Download paused
    :statuscode 500: Server error
    :resheader Content-Type: application/json

    **Example response:**

    .. code-block:: json

        {
            "message": "Download paused"
        }


.. http:post:: /resume-download

    Request resuming the download process.

    **Response:**

    :statuscode 200: Download resumed
    :statuscode 500: Server error
    :resheader Content-Type: application/json

    **Example response:**

    .. code-block:: json

        {
            "message": "Download resumed"
        }


.. http:post:: /clear-queue

    Request clearing the download queue.

    **Response:**

    :statuscode 200: Queue cleared
    :statuscode 400: No settings provided from webui 
    :statuscode 500: Server error
    :resheader Content-Type: application/json

    **Example response:**

    .. code-block:: json

        {
            "message": "Queue cleared"
        }



.. http:post:: /remove-item

    Request removing a specific item from the queue by somedl_id.

    **Request body:**

    .. code-block:: json

        {
            "somedl_id": "17806724760830844000001"
        }

    **Response:**

    :statuscode 200: Item Removed
    :statuscode 500: Server error
    :resheader Content-Type: application/json

    **Example response:**

    .. code-block:: json

        {
            "message": "Item removed"
        }

YouTube Search
--------------

.. http:post:: /yt-download

    Adding a YouTube URL to the download queue. 
    Optionally also takes a "artist_preset" dict, which specifies if singles and or titles with other artists should also be downloaded when the URL is an artist/band channel URL.

    **Request body:**

    :<json string url: Single URL as a string. To download multiple URLs at once, use ``/add``.
    :<json bool artist_preset.singles: Whether to include singles.
    :<json bool artist_preset.other: Whether to include albums and singles with other artists as the main artist.

    .. code-block:: json

        {
            "url": "http://...",
            "artist_preset": {
                "singles": false,
                "other": false
            }
        }
    

    **Behavior:**

    - Expands input using ``generateSongList()``
    - Adds each song to ``song_list_queue`` for download

    **Responses:**

    :statuscode 200: Sucessfully added url
    :statuscode 400: Missing or invalid "url" field
    :statuscode 500: Failed to generate song list, internal server error.

    :resheader Content-Type: application/json

    :>json list song_list: List of items to download with some prefetched metadata.


    **Success response (200):**

    .. code-block:: json

        {
            "song_list": [
                {
                    "album_id": "MPREb_B9YcEZY20ip",
                    "album_name": "Dark Waters",
                    "artist_all_names": [
                        "Delain"
                    ],
                    "artist_id": "UCPIXyGsEUrGIz7olJ1d7-Ig",
                    "artist_name": "Delain",
                    "lyrics_id": "MPLYt_B9YcEZY20ip-1",
                    "original_url_id": "WOZOwTG9dmU",
                    "somedl_id": "17806739333906158000001",
                    "song_id": "WOZOwTG9dmU",
                    "song_title": "Hideaway Paradise",
                    "song_title_clean": "Hideaway Paradise",
                    "video_type": "MUSIC_VIDEO_TYPE_ATV",
                    "video_type_original": "MUSIC_VIDEO_TYPE_ATV",
                    "yt_url": "https://www.youtube.com/watch?v=WOZOwTG9dmU"
                }
            ]
        }

    **Error response (400):**

    .. code-block:: json

        {
            "error": "No item"
        }

    **Error response (500):**

    .. code-block:: json

        {
            "error": "Failed to generate song list, internal server error"
        }




.. http:post:: /yt-search

    Search for songs/albums/artists on youtube music via a search request. Uses the `ytmusicapi search function <https://ytmusicapi.readthedocs.io/en/stable/reference/search.html#ytmusicapi.YTMusic.search>`_.

    **Request body:**

    :<json string search_query: Search query.
    :<json string filter: Search filter (Options: ``songs``, ``albums``, ``artists``).

    .. code-block:: json

        {
            "search_query": "string",
            "filter": "songs"
        }
    


    **Responses:**

    :statuscode 200: Successfull lookup
    :statuscode 400: Missing or invalid "search_query" or "filter" field
    :statuscode 500: Failed to generate song list, internal server error

    :resheader Content-Type: application/json

    :>json list result: List of songs/albums/artists. Maximum length is 20 items.


    **Success response (filter = "songs"):**

    .. code-block:: json

        {
            "result": [
                {
                    "album": {
                        "id": "MPREb_iUk3tvhGHje",
                        "name": "We Are The Others"
                    },
                    "artists": [
                        {
                            "id": "UCPIXyGsEUrGIz7olJ1d7-Ig",
                            "name": "Delain"
                        }
                    ],
                    "category": "Songs",
                    "duration": "3:18",
                    "duration_seconds": 198,
                    "inLibrary": false,
                    "isExplicit": false,
                    "pinnedToListenAgain": false,
                    "resultType": "song",
                    "thumbnails": [
                        {
                            "height": 60,
                            "url": "https://yt3.googleusercontent.com/uEzYLh0FvVEV07ifl2boE6il0gjb7UykMCeWDO6wCV6Mr9FwMx6k_uwYO2SDJLRAdxPmQthHpoWLVQA=w60-h60-l90-rj",
                            "width": 60
                        },
                        {
                            "height": 120,
                            "url": "https://yt3.googleusercontent.com/uEzYLh0FvVEV07ifl2boE6il0gjb7UykMCeWDO6wCV6Mr9FwMx6k_uwYO2SDJLRAdxPmQthHpoWLVQA=w120-h120-l90-rj",
                            "width": 120
                        }
                    ],
                    "title": "We Are the Others",
                    "videoId": "kErCh2TwPlU",
                    "videoType": "MUSIC_VIDEO_TYPE_ATV",
                    "views": "1.8M",
                    "year": null
                }
            ]
        }
    
    **Success response (filter = "albums"):**

    .. code-block:: json

        {
            "result": [
                {
                    "artists": [
                        {
                            "id": "UCxgN32UVVztKAQd2HkXzBtw",
                            "name": "Linkin Park"
                        }
                    ],
                    "browseId": "MPREb_d1UkStdzUrN",
                    "category": "Albums",
                    "duration": null,
                    "isExplicit": true,
                    "playlistId": "OLAK5uy_miCUHAHUPqc21dc-Vs7KTxbbqqzFCl68c",
                    "resultType": "album",
                    "thumbnails": [
                        {
                            "height": 60,
                            "url": "https://yt3.googleusercontent.com/R-yqivSHsR8ZWpKMy2vplo6LEK-c0XVA7SzRRHR0eUYa-Gazo1VnbVnmN1ifymUOuCmW5yxjFlNv-rBv=w60-h60-l90-rj",
                            "width": 60
                        },
                        {
                            "height": 120,
                            "url": "https://yt3.googleusercontent.com/R-yqivSHsR8ZWpKMy2vplo6LEK-c0XVA7SzRRHR0eUYa-Gazo1VnbVnmN1ifymUOuCmW5yxjFlNv-rBv=w120-h120-l90-rj",
                            "width": 120
                        },
                        {
                            "height": 226,
                            "url": "https://yt3.googleusercontent.com/R-yqivSHsR8ZWpKMy2vplo6LEK-c0XVA7SzRRHR0eUYa-Gazo1VnbVnmN1ifymUOuCmW5yxjFlNv-rBv=w226-h226-l90-rj",
                            "width": 226
                        },
                        {
                            "height": 544,
                            "url": "https://yt3.googleusercontent.com/R-yqivSHsR8ZWpKMy2vplo6LEK-c0XVA7SzRRHR0eUYa-Gazo1VnbVnmN1ifymUOuCmW5yxjFlNv-rBv=w544-h544-l90-rj",
                            "width": 544
                        }
                    ],
                    "title": "From Zero",
                    "type": "Album",
                    "year": "2024"
                }
            ]
        }
    
    **Success response (filter = "artists"):**

    .. code-block:: json

        {
            "result": [
                {
                "artist": "Gojira",
                "browseId": "UCPdbkw3S_0ZSHAqlnxo9E_g",
                "category": "Artists",
                "radioId": "RDEM10r_le6ENKoy-v2QrI4jUQ",
                "resultType": "artist",
                "shuffleId": "RDAO10r_le6ENKoy-v2QrI4jUQ",
                "thumbnails": [
                        {
                            "height": 60,
                            "url": "https://yt3.googleusercontent.com/jAr4PjfJewcE3Tw0eKZhZo1EnKJ2jM6Melc2mdnVB8MilEavHTm6dCI1gMddTqExRUUOSljpgqAYZJhc=w60-h60-l90-rj",
                            "width": 60
                        },
                        {
                            "height": 120,
                            "url": "https://yt3.googleusercontent.com/jAr4PjfJewcE3Tw0eKZhZo1EnKJ2jM6Melc2mdnVB8MilEavHTm6dCI1gMddTqExRUUOSljpgqAYZJhc=w120-h120-l90-rj",
                            "width": 120
                        }
                    ]
                }
            ]
        }



.. http:post:: /yt-get-album

    Look up content of album by album ID / playlist ID. Uses the `ytmusicapi get_playlist function <https://ytmusicapi.readthedocs.io/en/stable/reference/playlists.html#ytmusicapi.YTMusic.get_playlist>`_.

    **Request body:**

    :<json string album_id: Album/playlist ID.

    .. code-block:: json

        {
            "album_id": "OLAK5uy_miCUHAHUPqc21dc-Vs7KTxbbqqzFCl68c",
        }
    


    **Responses:**

    :statuscode 200: Successfull lookup
    :statuscode 400: Missing ``album_id``
    :statuscode 500: Ytmusicapi error

    :resheader Content-Type: application/json

    :>json dict result: Album information.


    **Success response (200):**

    .. code-block:: json

        {
            "result": {
                "description": null,
                "duration": null,
                "duration_seconds": 2855,
                "id": "OLAK5uy_nHqy1pH4pgb4_3ChdbJuLi4lQ_QyP2h38",
                "owned": false,
                "privacy": "PUBLIC",
                "related": [],
                "thumbnails": [],
                "title": "Moonbathers",
                "trackCount": 11,
                "tracks": [
                    {
                        "album": {
                            "id": "MPREb_NYSc5fVwzSO",
                            "name": "Moonbathers"
                        },
                        "artists": [
                            {
                                "id": "UCPIXyGsEUrGIz7olJ1d7-Ig",
                                "name": "Delain"
                            }
                        ],
                        "communityVoteStatus": null,
                        "creditsBrowseId": "MPTCDL4AzwmfqJY",
                        "duration": "5:10",
                        "duration_seconds": 310,
                        "feedbackTokens": {
                            "add": null,
                            "remove": "AB9zfpIb1X5qDWjfQDvc3eBslX9rQYqUNxMxPUPAl2NgocQqtW9IWrWNXLKva8HLRipxggXxim4lL_5QJvadboa0hzAdvzp-Xw"
                        },
                        "inLibrary": false,
                        "isAvailable": true,
                        "isExplicit": false,
                        "likeStatus": "INDIFFERENT",
                        "pinnedToListenAgain": false,
                        "thumbnails": [
                            {
                                "height": 60,
                                "url": "https://yt3.googleusercontent.com/CxnYEyfnKAojje1sbDSsgFGatebvhiLrwwJ6EkXeIEZuARhxvOKs5LC7x639nVcurDH58mrWW1seXYkQ=w60-h60-l90-rj",
                                "width": 60
                            },
                            {
                                "height": 120,
                                "url": "https://yt3.googleusercontent.com/CxnYEyfnKAojje1sbDSsgFGatebvhiLrwwJ6EkXeIEZuARhxvOKs5LC7x639nVcurDH58mrWW1seXYkQ=w120-h120-l90-rj",
                                "width": 120
                            }
                        ],
                        "title": "Hands of Gold (feat. Alissa White-Gluz)",
                        "videoId": "DL4AzwmfqJY",
                        "videoType": "MUSIC_VIDEO_TYPE_ATV",
                        "views": null
                    }
                ],
                "views": null
            }
        }
    



.. http:post:: /yt-get-album-browse-id

    Look up content of album by browse ID. Uses the `ytmusicapi get_album <https://ytmusicapi.readthedocs.io/en/stable/reference/browsing.html#ytmusicapi.YTMusic.get_album>`_ and `ytmusicapi get_playlist function <https://ytmusicapi.readthedocs.io/en/stable/reference/playlists.html#ytmusicapi.YTMusic.get_playlist>`_.

    **Request body:**

    :<json string album_id: Album browse ID.
    :<json bool return_album_data: Set true if you also want the data gathered from ``get_album()``.

    .. code-block:: json

        {
            "album_id": "UCPdbkw3S_0ZSHAqlnxo9E_g",
            "return_album_data": "true"
        }
    


    **Responses:**

    :statuscode 200: Successfull lookup
    :statuscode 400: Missing ``album_id``
    :statuscode 500: Ytmusicapi error

    :resheader Content-Type: application/json

    :>json dict result: Album information from ytmusicapi ``get_playlist()``.
    :>json dict album_data: Album information from ytmusicapi ``get_album()``.


    **Success response (200):**

    .. code-block:: json

        {
            "album_data": {
                "artists": [
                    {
                        "id": "UCPIXyGsEUrGIz7olJ1d7-Ig",
                        "name": "Delain"
                    }
                ],
                "audioPlaylistId": "OLAK5uy_neK6NwgDYtQ9uDuj1P4nBCRLM3VOtEdj8",
                "description": "We Are the Others is the third studio album by the Dutch symphonic metal band Delain. It was released in the Benelux and Germany on 1 June 2012 and in the United Kingdom and France on 4 June by CNR Music, who took over Delain when Warner Music refused to release We Are the Others. The album was released in the US on 3 July. The first single, \"Get the Devil Out of Me\", was released on 13 April. The second single \"We Are The Others\" and its video was released on 11 September 2012. This is the first album by Delain without any studio songs with guest vocalist Marko Hietala. Live versions of \"The Gathering\" and \"Control the Storm\" are featured on the special edition of the album with Hietala singing his parts live.\n\nFrom Wikipedia (",
                "duration": "47 minutes",
                "duration_seconds": 2865,
                "isExplicit": false,
                "likeStatus": "INDIFFERENT",
                "thumbnails": [
                    {
                        "height": 60,
                        "url": "https://yt3.googleusercontent.com/uEzYLh0FvVEV07ifl2boE6il0gjb7UykMCeWDO6wCV6Mr9FwMx6k_uwYO2SDJLRAdxPmQthHpoWLVQA=w60-h60-l90-rj",
                        "width": 60
                    },
                    {
                        "height": 120,
                        "url": "https://yt3.googleusercontent.com/uEzYLh0FvVEV07ifl2boE6il0gjb7UykMCeWDO6wCV6Mr9FwMx6k_uwYO2SDJLRAdxPmQthHpoWLVQA=w120-h120-l90-rj",
                        "width": 120
                    },
                    {
                        "height": 226,
                        "url": "https://yt3.googleusercontent.com/uEzYLh0FvVEV07ifl2boE6il0gjb7UykMCeWDO6wCV6Mr9FwMx6k_uwYO2SDJLRAdxPmQthHpoWLVQA=w226-h226-l90-rj",
                        "width": 226
                    },
                    {
                        "height": 544,
                        "url": "https://yt3.googleusercontent.com/uEzYLh0FvVEV07ifl2boE6il0gjb7UykMCeWDO6wCV6Mr9FwMx6k_uwYO2SDJLRAdxPmQthHpoWLVQA=w544-h544-l90-rj",
                        "width": 544
                    }
                ],
                "title": "We Are The Others",
                "trackCount": 12,
                "tracks": [
                    {
                        "album": "We Are The Others",
                        "artists": [
                            {
                                "id": "UCPIXyGsEUrGIz7olJ1d7-Ig",
                                "name": "Delain"
                            }
                        ],
                        "communityVoteStatus": null,
                        "creditsBrowseId": "MPTCNDM_VcVwh-k",
                        "duration": "4:35",
                        "duration_seconds": 275,
                        "feedbackTokens": {
                            "add": null,
                            "remove": "AB9zfpLjKs8jZCF8fTwquabO9fZ5VfNyvBm-pnj-yJzEH51D6ROjfhc4Ptvy5gm1WpBXYiwFURQyIAPe3tqn3GasIoOkUwuMWQ"
                        },
                        "inLibrary": false,
                        "isAvailable": true,
                        "isExplicit": false,
                        "likeStatus": "INDIFFERENT",
                        "pinnedToListenAgain": false,
                        "thumbnails": null,
                        "title": "Mother Machine",
                        "trackNumber": 1,
                        "videoId": "NDM_VcVwh-k",
                        "videoType": "MUSIC_VIDEO_TYPE_ATV",
                        "views": "430K plays"
                    }
                ],
                "type": "Album",
                "year": "2012"
            },
            "result": {
                "description": null,
                "duration": null,
                "duration_seconds": 2865,
                "id": "OLAK5uy_neK6NwgDYtQ9uDuj1P4nBCRLM3VOtEdj8",
                "owned": false,
                "privacy": "PUBLIC",
                "related": [],
                "thumbnails": [],
                "title": "We Are The Others",
                "trackCount": 12,
                "tracks": [
                    {
                        "album": {
                            "id": "MPREb_iUk3tvhGHje",
                            "name": "We Are The Others"
                        },
                        "artists": [
                            {
                                "id": "UCPIXyGsEUrGIz7olJ1d7-Ig",
                                "name": "Delain"
                            }
                        ],
                        "communityVoteStatus": null,
                        "creditsBrowseId": "MPTCNDM_VcVwh-k",
                        "duration": "4:35",
                        "duration_seconds": 275,
                        "feedbackTokens": {
                            "add": null,
                            "remove": "AB9zfpKf5rEkvLSDyGrB6_oRyFEv1l6pOVhDtoe_G2fJ9XpYgrmJrsKt7aJI6ce4rS14ycYFGkM0bQv6YyPEw6-pmywLGT2rKg"
                        },
                        "inLibrary": false,
                        "isAvailable": true,
                        "isExplicit": false,
                        "likeStatus": "INDIFFERENT",
                        "pinnedToListenAgain": false,
                        "thumbnails": [
                            {
                                "height": 60,
                                "url": "https://yt3.googleusercontent.com/uEzYLh0FvVEV07ifl2boE6il0gjb7UykMCeWDO6wCV6Mr9FwMx6k_uwYO2SDJLRAdxPmQthHpoWLVQA=w60-h60-l90-rj",
                                "width": 60
                            },
                            {
                                "height": 120,
                                "url": "https://yt3.googleusercontent.com/uEzYLh0FvVEV07ifl2boE6il0gjb7UykMCeWDO6wCV6Mr9FwMx6k_uwYO2SDJLRAdxPmQthHpoWLVQA=w120-h120-l90-rj",
                                "width": 120
                            }
                        ],
                        "title": "Mother Machine",
                        "videoId": "NDM_VcVwh-k",
                        "videoType": "MUSIC_VIDEO_TYPE_ATV",
                        "views": null
                    }
                ],
                "views": null
            }
        }


.. http:post:: /yt-get-artist

    Look up artist by artist ID. Uses the `ytmusicapi get_playlist function <https://ytmusicapi.readthedocs.io/en/stable/reference/browsing.html#ytmusicapi.YTMusic.get_artist>`_.

    **Request body:**

    :<json string artist_id: Artist ID.

    .. code-block:: json

        {
            "artist_id": "UCRAHc1Aild5p1Zmy2rAgVmA",
        }
    


    **Responses:**

    :statuscode 200: Successfull lookup
    :statuscode 400: Missing ``artist_id``
    :statuscode 500: Ytmusicapi error

    :resheader Content-Type: application/json

    :>json dict result: Artist information, including lists of albums and singles.


    **Success response (200):**

    .. code-block:: json

        {
            "result": {
                "albums": {
                    "browseId": "MPADUCRAHc1Aild5p1Zmy2rAgVmA",
                    "params": "ggMIegYIARoCAQI%3D",
                    "results": [
                        {
                            "browseId": "MPREb_QUSFPk9bVbr",
                            "playlistId": "OLAK5uy_nAXNlW2rUoESvV8iAAdhTk7shLE2OA4TY",
                            "thumbnails": [
                                {
                                    "height": 226,
                                    "url": "https://yt3.googleusercontent.com/YxmTS8kRUvzKNgFWCRPtbXU4Qgyf6hSs7STYPGN7aI5mNKD3LNXOHuZWD5B9MLeiyn2J_RUp3VYsEJiV=w226-h226-l90-rj",
                                    "width": 226
                                },
                                {
                                    "height": 544,
                                    "url": "https://yt3.googleusercontent.com/YxmTS8kRUvzKNgFWCRPtbXU4Qgyf6hSs7STYPGN7aI5mNKD3LNXOHuZWD5B9MLeiyn2J_RUp3VYsEJiV=w544-h544-l90-rj",
                                    "width": 544
                                }
                            ],
                            "title": "Borderland",
                            "type": "Album",
                            "year": "2025"
                        }
                    ]
                },
                "channelId": "UC-7JFVd4iyli6EB-ycLUEfA",
                "description": "With “Borderland,” the title of the album couldn’t have been chosen more fittingly. Throughout their career, spanning over more than three decades, AMORPHIS -- Tomi Joutsen (vocals), Esa Holopainen (guitars), Tomi Koivusaari (guitars), Olli-Pekka Laine (bass), Santeri Kallio (keyboards) & Jan Rechberger (drums & percussion) -- have been an ever-evolving act, wandering on an boundary-pushing path. From their death metal debut “Karelian Isthmus” over genre-defining mid-90s melodic death works like “Tales From The Thousand Lakes” and “Elegy” as well as the melodic 2000’s grandeur of “Eclipse” or “Skyforger” to records combining the best of all prior eras to refreshing new soundscapes: Whatever this group works on promises long-range success.\nWith 2022’s “Halo,” the Finn’s were rewarded for their researching musical approach once again: The album marked AMORPHIS’ sixth no. 1 album in Finland, even cracked the top 3 of the official German album chart, and last but not least the sextet took home two awards from the prestigious Emma Gaala (“Band of the Year” & “Export of the Year”).\nRather than rushing into a follow-up, the band chose to step back from live performances and focus fully on their next chapter. The result is “Borderland” - a meticulously crafted opus that builds on their celebrated recent era, while seamlessly weaving in new, timely elements. It’s a bold, organic continuation of their journey, shaped by experience and guided by vision.",
                "monthlyListeners": "217K",
                "name": "Amorphis",
                "radioId": "RDEMEOlPD_Xv5fk2zPgOg40mJA",
                "shuffleId": "RDAOEOlPD_Xv5fk2zPgOg40mJA",
                "singles": {
                    "browseId": null,
                    "results": [
                        {
                            "browseId": "MPREb_7kmkmlGU5Uc",
                            "thumbnails": [
                                {
                                    "height": 226,
                                    "url": "https://yt3.googleusercontent.com/MyDSH5B2buZV6T8MSNySZXmomA0C4L2RRH39bYZ8eOc5ZPhnJIJ275-WFKTv5EeLYUwrhRiYtCMrPuoi=w226-h226-l90-rj",
                                    "width": 226
                                },
                                {
                                    "height": 544,
                                    "url": "https://yt3.googleusercontent.com/MyDSH5B2buZV6T8MSNySZXmomA0C4L2RRH39bYZ8eOc5ZPhnJIJ275-WFKTv5EeLYUwrhRiYtCMrPuoi=w544-h544-l90-rj",
                                    "width": 544
                                }
                            ],
                            "title": "Crowned In Crimson (From “Son of Revenge - The Story of Kalevala”)",
                            "type": "Single",
                            "year": "2025"
                        }
                    ]
                },
                "songs": {
                    "browseId": "VLOLAK5uy_n3UjAfChqR0t4DOo84TJ1RoxBdISFQdrM",
                    "results": [
                        {
                            "album": {
                                "id": "MPREb_scOnQlj1GXx",
                                "name": "Dancing Shadow"
                            },
                            "artists": [
                                {
                                    "id": "UCRAHc1Aild5p1Zmy2rAgVmA",
                                    "name": "Amorphis"
                                }
                            ],
                            "communityVoteStatus": null,
                            "creditsBrowseId": "MPTCAah4nfXosDs",
                            "inLibrary": false,
                            "isAvailable": true,
                            "isExplicit": false,
                            "likeStatus": "INDIFFERENT",
                            "pinnedToListenAgain": false,
                            "thumbnails": [
                                {
                                    "height": 60,
                                    "url": "https://yt3.googleusercontent.com/UoNKvTZYnErQb-KZRpKgZHlQgfOEheXeTTi0TZacpXNTXGbcGARz2G46L6LOrtkI465kwK9jd2vahtO_QQ=w60-h60-l90-rj",
                                    "width": 60
                                },
                                {
                                    "height": 120,
                                    "url": "https://yt3.googleusercontent.com/UoNKvTZYnErQb-KZRpKgZHlQgfOEheXeTTi0TZacpXNTXGbcGARz2G46L6LOrtkI465kwK9jd2vahtO_QQ=w120-h120-l90-rj",
                                    "width": 120
                                }
                            ],
                            "title": "Dancing Shadow",
                            "videoId": "Aah4nfXosDs",
                            "videoType": "MUSIC_VIDEO_TYPE_ATV",
                            "views": null
                        }
                    ]
                },
                "subscribed": false,
                "subscribers": "67.8K",
                "thumbnails": [
                    {
                        "height": 225,
                        "url": "https://lh3.googleusercontent.com/ohpZ6WZZn-myNFj4uGgaj06p2P80j-FHJLRVrSYa5KQy4RCeoqFc4UJdfSx463dXnJCQQcwxO822SWM=w540-h225-p-l90-rj",
                        "width": 540
                    },
                    {
                        "height": 340,
                        "url": "https://lh3.googleusercontent.com/ohpZ6WZZn-myNFj4uGgaj06p2P80j-FHJLRVrSYa5KQy4RCeoqFc4UJdfSx463dXnJCQQcwxO822SWM=w816-h340-p-l90-rj",
                        "width": 816
                    },
                    {
                        "height": 600,
                        "url": "https://lh3.googleusercontent.com/ohpZ6WZZn-myNFj4uGgaj06p2P80j-FHJLRVrSYa5KQy4RCeoqFc4UJdfSx463dXnJCQQcwxO822SWM=w1440-h600-p-l90-rj",
                        "width": 1440
                    },
                    {
                        "height": 800,
                        "url": "https://lh3.googleusercontent.com/ohpZ6WZZn-myNFj4uGgaj06p2P80j-FHJLRVrSYa5KQy4RCeoqFc4UJdfSx463dXnJCQQcwxO822SWM=w1920-h800-p-l90-rj",
                        "width": 1920
                    },
                    {
                        "height": 1200,
                        "url": "https://lh3.googleusercontent.com/ohpZ6WZZn-myNFj4uGgaj06p2P80j-FHJLRVrSYa5KQy4RCeoqFc4UJdfSx463dXnJCQQcwxO822SWM=w2880-h1200-p-l90-rj",
                        "width": 2880
                    }
                ],
                "videos": {
                    "browseId": "VLOLAK5uy_mogZ9cmuGDCgiCo3oLQoswGpW_sqRB6po",
                    "params": "ggMCCAI%3D",
                    "results": [
                        {
                            "artists": [
                                {
                                    "id": "UCRAHc1Aild5p1Zmy2rAgVmA",
                                    "name": "Amorphis"
                                }
                            ],
                            "playlistId": "OLAK5uy_mogZ9cmuGDCgiCo3oLQoswGpW_sqRB6po",
                            "thumbnails": [
                                {
                                    "height": 180,
                                    "url": "https://i.ytimg.com/vi/V9epeO7r8vs/hqdefault.jpg?sqp=-oaymwEWCMACELQBIAQqCghQEJADGFogjgJIWg&rs=AMzJL3mcZj5qoJKgNUbPGicc5b876D3mXA",
                                    "width": 320
                                }
                            ],
                            "title": "AMORPHIS - House of Sleep (OFFICIAL MUSIC VIDEO)",
                            "videoId": "V9epeO7r8vs",
                            "views": "836K"
                        }
                    ]
                },
                "views": "34,070,006 views"
            }
        }


Setlist
-------

.. http:post:: /setlist-artist

    Searching for a artist by search query on `setlist.fm <https://api.setlist.fm/docs/1.0/index.html>`_.

    **Request body:**

    :<json string search_query: Artist/Band name.

    .. code-block:: json

        {
            "search_query": "Artist/Band name",
        }
    

    **Responses:**

    :statuscode 200: Successfull lookup
    :statuscode 400: Missing or invalid ``search_query`` field
    :statuscode 500: Internal server error

    :resheader Content-Type: application/json

    :>json list result: List of artists.


    **Success response (200):**

    .. code-block:: json

        {
            "result": {
                "artist": [
                    {
                        "disambiguation": "Dutch symphonic metal band",
                        "mbid": "3b0e8f01-3fd9-4104-9532-1e4b526ce562",
                        "name": "Delain",
                        "sortName": "Delain",
                        "url": "https://www.setlist.fm/setlists/delain-1bd6fd7c.html"
                    },
                    {
                        "disambiguation": "",
                        "mbid": "0470ff3e-3354-4b2a-a46d-e3ea50bed60b",
                        "name": "Delain feat. Rob van der Loo, Sander Zoer, Guus Eikens",
                        "sortName": "Delain feat. Loo, Rob van der, Zoer, Sander, Eikens, Guus",
                        "url": "https://www.setlist.fm/setlists/delain-feat-rob-van-der-loo-sander-zoer-guus-eikens-3bcdc0e4.html"
                    }
                ],
                "itemsPerPage": 30,
                "page": 1,
                "total": 9,
                "type": "artists"
            }
        }


.. http:post:: /setlist-mbid

    Searching for a setlist by mbid on `setlist.fm <https://api.setlist.fm/docs/1.0/index.html>`_.

    **Request body:**

    :<json string mbid: MusicBrainz ID of artist, aquired from ``/setlist-artist``.
    :<json int page: Setlist page.

    .. code-block:: json

        {
            "mbid": "Artist/Band name",
            "page": "1"
        }
    

    **Responses:**

    :statuscode 200: Successfull lookup
    :statuscode 400: Missing or invalid ``mbid`` field
    :statuscode 500: Internal server error

    :resheader Content-Type: application/json

    :>json list result: List of setlists.


    **Success response (200):**

    .. code-block:: json

        {
            "result": {
                "itemsPerPage": 20,
                "page": 1,
                "setlist": [
                    {
                        "artist": {
                            "disambiguation": "Dutch symphonic metal band",
                            "mbid": "3b0e8f01-3fd9-4104-9532-1e4b526ce562",
                            "name": "Delain",
                            "sortName": "Delain",
                            "url": "https://www.setlist.fm/setlists/delain-1bd6fd7c.html"
                        },
                        "eventDate": "18-10-2025",
                        "id": "5b59e7ec",
                        "lastUpdated": "2025-10-19T07:37:47.657+0000",
                        "sets": {
                            "set": [
                                {
                                    "song": [
                                        {
                                            "name": "The Cold"
                                        },
                                        {
                                            "name": "Suckerpunch"
                                        },
                                        {
                                            "name": "The Reaping"
                                        },
                                        {
                                            "name": "Dance With the Devil"
                                        },
                                        {
                                            "name": "Burning Bridges"
                                        },
                                        {
                                            "name": "Creatures"
                                        },
                                        {
                                            "name": "Stardust"
                                        },
                                        {
                                            "info": "Acoustic",
                                            "name": "Start Swimming"
                                        },
                                        {
                                            "name": "Underland"
                                        },
                                        {
                                            "name": "Get the Devil Out of Me"
                                        },
                                        {
                                            "name": "Your Body Is a Battleground",
                                            "with": {
                                                "disambiguation": "Italian-born singer based in Finland",
                                                "mbid": "1dc6c8c8-548f-4d1a-87ea-e557cb7064b9",
                                                "name": "Paolo Ribaldini",
                                                "sortName": "Ribaldini, Paolo",
                                                "url": "https://www.setlist.fm/setlists/paolo-ribaldini-13cac925.html"
                                            }
                                        },
                                        {
                                            "name": "Queen of Shadow",
                                            "with": {
                                                "disambiguation": "Italian-born singer based in Finland",
                                                "mbid": "1dc6c8c8-548f-4d1a-87ea-e557cb7064b9",
                                                "name": "Paolo Ribaldini",
                                                "sortName": "Ribaldini, Paolo",
                                                "url": "https://www.setlist.fm/setlists/paolo-ribaldini-13cac925.html"
                                            }
                                        },
                                        {
                                            "name": "The Gathering",
                                            "with": {
                                                "disambiguation": "Italian-born singer based in Finland",
                                                "mbid": "1dc6c8c8-548f-4d1a-87ea-e557cb7064b9",
                                                "name": "Paolo Ribaldini",
                                                "sortName": "Ribaldini, Paolo",
                                                "url": "https://www.setlist.fm/setlists/paolo-ribaldini-13cac925.html"
                                            }
                                        },
                                        {
                                            "name": "Don't Let Go"
                                        },
                                        {
                                            "name": "Moth to a Flame"
                                        },
                                        {
                                            "name": "Not Enough"
                                        },
                                        {
                                            "name": "Invictus",
                                            "with": {
                                                "disambiguation": "Italian-born singer based in Finland",
                                                "mbid": "1dc6c8c8-548f-4d1a-87ea-e557cb7064b9",
                                                "name": "Paolo Ribaldini",
                                                "sortName": "Ribaldini, Paolo",
                                                "url": "https://www.setlist.fm/setlists/paolo-ribaldini-13cac925.html"
                                            }
                                        },
                                        {
                                            "name": "We Are the Others"
                                        },
                                        {
                                            "cover": {
                                                "disambiguation": "",
                                                "mbid": "f7aad4fb-9286-4f60-aae8-5da5922f17cf",
                                                "name": "Hans Zimmer & Lisa Gerrard",
                                                "sortName": "Zimmer, Hans & Gerrard, Lisa",
                                                "url": "https://www.setlist.fm/setlists/hans-zimmer-and-lisa-gerrard-73d6b635.html"
                                            },
                                            "name": "Now We Are Free",
                                            "tape": true
                                        }
                                    ]
                                }
                            ]
                        },
                        "tour": {
                            "name": "One Last Dance with the Devil"
                        },
                        "url": "https://www.setlist.fm/setlist/delain/2025/leffe-stage-enschede-netherlands-5b59e7ec.html",
                        "venue": {
                            "city": {
                                "coords": {
                                    "lat": 52.218333,
                                    "long": 6.895833
                                },
                                "country": {
                                    "code": "NL",
                                    "name": "Netherlands"
                                },
                                "id": "2756071",
                                "name": "Enschede",
                                "state": "Overijssel",
                                "stateCode": "15"
                            },
                            "id": "2bde9886",
                            "name": "Leffe Stage",
                            "url": "https://www.setlist.fm/venue/leffe-stage-enschede-netherlands-2bde9886.html"
                        },
                        "versionId": "g33660c71"
                    },
                    
                ],
                "total": 833,
                "type": "setlists"
            }
        }

Settings
--------

.. http:get:: /settings-read

    Returns current SomeDL settings. Also includes configuration options not in the config file.

    **Response:**

    :statuscode 200: Successfull returned config
    :resheader Content-Type: application/json

    **Example response:**

    .. code-block:: json

        {
            "config": {
                "api": {
                    "deezer": true,
                    "genius": true,
                    "genius_album_check": true,
                    "genius_token": "",
                    "genius_use_official": false,
                    "max_retry": 3,
                    "mb_retry_artist_name_only": false,
                    "musicbrainz": true
                },
                "download": {
                    "always_search_by_query": false,
                    "check_if_file_exists": true,
                    "cookies_from_browser": "",
                    "cookies_path": "",
                    "disable_download": false,
                    "download_archive": "",
                    "fetch_albums": false,
                    "format": "m4a",
                    "id3_version": 3,
                    "include_other_artists": false,
                    "include_singles": false,
                    "number_downloaders": 1,
                    "output": "{album_artist}/{album_artist} - {song}",
                    "output_dir": "/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/",
                    "prefer_playlist": false,
                    "quality": 5,
                    "queue_size": 2,
                    "range": [],
                    "sleep": 3,
                    "sleep_warn": true,
                    "strict_url_download": false,
                    "sync_files": [
                        "/home/chemgull/.config/SomeDL/myPlaylist3_sync.json"
                    ]
                },
                "logging": {
                    "config_version": 7,
                    "download_report": 2,
                    "level": "INFO",
                    "log_level": 4
                },
                "metadata": {
                    "album_artist": true,
                    "artist_separator": "; ",
                    "copyright": true,
                    "cover_art_file": false,
                    "cover_art_size": "l",
                    "ffmpeg_metadata": false,
                    "genre": true,
                    "isrc": true,
                    "lrc_file": false,
                    "lyrics": false,
                    "lyrics_fallback_source": "lrclib",
                    "lyrics_id3_synced_uslt_fallback": true,
                    "lyrics_source": "youtube",
                    "lyrics_type": "plain",
                    "multiple_artists": false,
                    "synced_lyrics_metadata": true
                },
                "webui": {
                    "browser": "chromium",
                    "host": "127.0.0.1",
                    "open_browser": false,
                    "port": 5000
                }
            }
        }


.. http:post:: /settings-apply

    Apply settings and save them to the config file.

    **Request body:**

    :<json dict settings: Settings dict.
    :<json bool update_active: Set true to also update configs of the current session and to false if you just want to modify the config file.


    .. code-block:: json

        {
            "settings": {
                "api": {
                    "musicbrainz": true,
                    "genius": true,
                    "genius_album_check": true,
                    "deezer": true,
                    "max_retry": 3
                },
                "metadata": {
                    "lyrics": false,
                    "copyright": true,
                    "isrc": true,
                    "genre": true,
                    "album_artist": true,
                    "multiple_artists": false,
                    "artist_separator": "; ",
                    "ffmpeg_metadata": false,
                    "cover_art_file": false,
                    "cover_art_size": "l",
                    "lyrics_type": "plain",
                    "synced_lyrics_metadata": true,
                    "lrc_file": false,
                    "lyrics_id3_synced_uslt_fallback": true,
                    "lyrics_source": "youtube",
                    "lyrics_fallback_source": "lrclib"
                },
                "download": {
                    "format": "mp3",
                    "quality": 5,
                    "id3_version": 3,
                    "output_dir": "/home/chemgull/Documents/Coding/Python/SomeDL/downloads/downloads/",
                    "output": "{album_artist}/{album_artist} - {song}",
                    "number_downloaders": 1,
                    "queue_size": 2,
                    "sleep": 3,
                    "cookies_path": "",
                    "cookies_from_browser": "",
                    "prefer_playlist": false,
                    "fetch_albums": false,
                    "check_if_file_exists": true,
                    "download_archive": "",
                    "sync_files": [
                        "/home/chemgull/.config/SomeDL/myPlaylist3_sync.json"
                    ]
                },
                "logging": {
                    "log_level": 4,
                    "download_report": 2
                },
                "webui": {
                    "host": "127.0.0.1",
                    "port": 5000,
                    "browser": "chromium",
                    "open_browser": false
                }
            },
            "update_active": true
        }

    **Response:**

    :statuscode 200: Success
    :statuscode 400: No settings provided
    :statuscode 500: Server error
    :resheader Content-Type: application/json

    **Example response:**

    .. code-block:: json

        {
            "message": "applied settings"
        }


WebUI configs
-------------

.. http:get:: /webui-load-config

    Loads current webui configs.

    **Response:**

    :statuscode 200: Successfull returned webui config
    :resheader Content-Type: application/json

    **Example response:**

    .. code-block:: json

        {
            "active_theme": "SomeDL Dark",
            "custom_themes": {
                "Another Theme": {
                    "theme": "dark",
                    "color-main": "#590058",
                    "color-main-highlight": "#711196",
                    "color-background": "#1e1c20",
                    "color-background-highlight": "#2d2b2f",
                    "color-button": "#0f0f0f",
                    "color-border": "#767676",
                    "color-text": "#FFFFFF",
                    "color-dlbar-1": "#711196",
                    "color-dlbar-2": "#ac3011"
                }
            }
        }


.. http:post:: /webui-save-config

    Save webui theme configs.

    **Request body:**

    :<json dict webui_settings: Settings dict.


    .. code-block:: json

        {
            "webui_settings": {
                "active_theme": "SomeDL Dark",
                "custom_themes": {
                    "My theme": {
                        "theme": "dark",
                        "color-main": "#590058",
                        "color-main-highlight": "#711196",
                        "color-background": "#1e1c20",
                        "color-background-highlight": "#2d2b2f",
                        "color-button": "#0f0f0f",
                        "color-border": "#767676",
                        "color-text": "#FFFFFF",
                        "color-dlbar-1": "#711196",
                        "color-dlbar-2": "#ac3011"
                    }
                }
            }
        }


    **Response:**

    :statuscode 200: Success
    :statuscode 400: No settings provided
    :statuscode 500: Server error
    :resheader Content-Type: application/json

    **Example response:**

    .. code-block:: json

        {
            "message": "applied settings"
        }