Features overview
=================

General & CLI
-------------

* Very simple usage
* No login or API tokens required. Just install and use.
* Free and open source forever
* Multiple download methods:

    * YouTube or YouTube Music Song URL
    * YouTube Playlist URL 
    * YouTube Album URL
    * YouTube Artist URL (full discography)

* Simple installation with pip
* Automatically downloads official audio instead of just extracting music video audio
* Complete metadata from multiple sources - way better than just relying on yt-dlp 

    * Song title
    * Artist name
    * Album name
    * Album artist name
    * High quality cover art (544x544)
    * Release date (Year)
    * Track number
    * Total track number
    * Genre
    * Lyrics sycned and plain
    * Copyright/Label 
    * ISRC
    * MusicBrainz artist ID (MBID)

* Several output formats: ``opus``, ``m4a``, ``mp3``, ``ogg``, ``flac``
* Sort downloads automatically into folders according to a template if desired:

    * For example: ``{album_artist}/{artist} - {song}``
    * Or more complex: ``{album_artist}/{year} - {album}/{track_pos} - {song}``
    * You can always change your storage template later with ``somedl new-template``

* Update your downloads based on one or more playlists with ``somedl sync``
* Add missing metadata to existing music files with ``somedl import``
* Download report - get a quick overview of the downloaded songs, including their metadata.
* And more

WebUI
-----
`Here <https://github.com/ChemistryGull/SomeDL/blob/main/docs/webui.md>`_ you can see a couple of pictures of the WebUI. Features of the WebUI include:

* Download songs directly from a browser-based graphical interface and track the progress
* Search for music within the WebUI using a YouTube Music-style interface.
* Look up concert setlists for bands and artists.
* View the download history for the current session
* Change settings directly from the WebUI
* Customize and theme the SomeDL WebUI to match your preferences