How To
======


How to get the most accurate metadata?
--------------------------------------

If you want the most accurate metadata, especially album name, it is best practice to download songs using YouTube Music album URLs, or by using the ``--fetch-album`` flag. 
Downloading an entire album this way ensures that all songs in that album get the same album name, and that songs are not split between regular, "extended edition", and "deluxe edition" variations.

How can I download an entire album with just a search query?
------------------------------------------------------------

You can use the ``--fetch-album`` flag.
With this flag, SomeDL downloads the entire album of every song in the download queue.
(Alternatively you can also provide a YouTube Music URL to an album.)

In the WebUI, search for the album in the YouTube Search tab and click on the album art to download the full album.

How can I download all songs from an artist?
--------------------------------------------

Use the URL of the band or artists youtube music channel:

.. code-block:: bash

    somedl https://music.youtube.com/channel/UCRAHc1Aild5p1Zmy2rAgVmA

By default, this will only download the albums of that band or artist. 
If you want to also include the singles, download them with ``--include-singles``.
If you also want to download albums or singles where the artist in question was not the main artist, set the flag ``--include-other-artists``

In the WebUI, search for the artist in the YouTube Search tab or click on the artists name on any album or song. 
On the artist page, click on the download button in the top right to download the full discography.


How can I change configurations?
--------------------------------

See :doc:`configuration`.



How do I download age-restricted songs?
---------------------------------------

You need to be logged into your age-verified YouTube account in your browser.

Then use:

.. code-block:: bash

    --cookies-from-browser firefox

This works best with Firefox and is the most straightforward method. If this doesn't work, you can export a
cookies file and use:

.. code-block:: bash

    --cookies "/path/to/cookies.txt"

Only use these flags when necessary. Heavy (ab)use of cookies with yt-dlp may lead
account bans. 

See the `the official yt-dlp docs <https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp>`_ for more info.



How can I exclude the cover art or change the cover art resolution?
-------------------------------------------------------------------

To not add the album art to the audio files, set ``cover_art_size`` to ``none`` in the configs (metadata section).
You can also choose a different resolution for the cover art, although the highest resolution is recommended for most users, since the cover art accounts for less than 10% of the total file size.
The default cover art is already the largest resolution provided by YouTube.


How can I slow the downloads down to prevent YouTube IP blocking?
-----------------------------------------------------------------

Fast downloading of a large number of songs may lead to your IP being blocked by YouTube. 
To prevent that, yt-dlp recommends using a sleep timer between downloads when downloading large numbers of files in a row 
(The exact limit is unknown. It is recommended to slow down downloads when downloading over 100 songs and highly recommended when downloading over 300 songs at once).

To set the sleep timer, run your command with the ``--sleep 10`` flag, with the number being the sleep time in seconds.
You can also permanently enable a sleep timer in the config file (``sleep`` entry).
In the WebUI, this setting is called "Sleep timer".
At least 5 seconds is recommended.
Setting ``sleep`` to a number higher than 0 lowers the number of downloaders to 1 as well.
The sleep timer is randomized, e.g. for ``sleep = 5`` the timer will be 5-9 seconds long.

So if you want to download a entire playlist with over 300 songs, it would be advised to start the download with a sleep timer of at the very least 5 seconds and let it download in the background.

From the CLI it is also possible to split up large playlists into chunks with the ``--range`` flag (e.g. ``--range :100`` to only download the first 100 songs).

More info on the `yt-dlp <https://github.com/yt-dlp/yt-dlp/wiki/Extractors#common-youtube-errors>`_ GitHub.


How can I download only a part of a playlist/album?
----------------------------------------------------

You can use the ``--range`` flag for that. This flag lets you use the Python slicing syntax to select the part of the list of songs you want to download (start:end:step). Examples:

- ``--range :3``   Downloads first 3 songs
- ``--range -3:``  Downloads last 3 songs
- ``--range 3:``   Downloads everything except the first 3 songs
- ``--range :-3``  Downloads everything except the last 3 songs
- ``--range 2:6``  Downloads songs 3 to 6
- ``--range ::2``  Downloads every second song


How do I use sync files?
------------------------

SomeDL has this feature to easily sync different playlists, each with their own configurations (e.g. output directory, file format, etc.). 
Let's say you have a concert playlist and you do not want to download the songs in it to your main library. 
That's where sync files come in handy.

A sync file is a JSON file that contains a list of playlists you want to download as well as configurations that override the ones in the config file. 
For example, if you want your concert playlists to be downloaded as Opus files to a different folder, add the ``format`` and ``output.dir`` entries. Such a sync file may look like this:

.. code-block:: json

    {
        "playlists": [
            "https://...",
            "https://...",
        ],
        "format": "best/opus",
        "output_dir": "/home/user/Music/Concert/"
    }


To create a new sync file, run:

.. code-block:: bash

    somedl sync --new-sync-file <"name for new sync file">

It is stored in the same directory as your config file. You can move it everywhere you want. To activate the new sync file, follow these steps:

1. Add the full file path of your sync file to the ``sync_files`` list in the config file.
2. Add the playlist URLs in the sync file. Each config file can contain as many URLs as you wish.
3. (Optional) Change other settings. All settings defined in ``somedl_config.toml`` can be overwritten by the values set in the sync file. ``output`` and ``output_dir`` are already added; you can remove those or add other ones, e.g. ``format`` etc. The file is in JSON format, adhere to its syntax. SomeDL will return an error if the syntax is not valid.
4. Use the sync file with ``somedl sync <sync target name>`` or just type ``somedl sync`` and select the synsc file.
   (e.g. ``myPlaylist_sync.json`` becomes ``myPlaylist``)

Be aware that you can only sync one sync file at a time. If you want to sync multiple playlists at once, add them all to one sync file.

SomeDL sync does not delete files from your library if it is deleted from the playlist due to the potential for data loss. If that's still a feature that you cannot live without, please open a feature request.


How can I avoid redownloading files when removing them from the download folder?
--------------------------------------------------------------------------------

You can use the download archive for this. Define a download archive file with ``--download-archive /path/to/archive.txt`` or by changing the ``download_archive`` config.
The name and filetype of the archive do not matter.
When such a file is defined, all video IDs of successful downloads will be added into that download archive and will be skipped on any future download attempts.

If you want to download a song that has already been downloaded with ``download_archive`` enabled, use the ``--redownload`` flag.


How can I change the output template for already downloaded files?
-------------------------------------------------------------------

You can type ``somedl new-template`` into the terminal.
It will ask you to provide the path to your files and the path to a new folder.
You will also have to provide the new output template.
You can choose between moving the files (less SSD writes) and copying files (safer in case something goes wrong).
You can also merge different storage templates in this way.

Below you can see the interactive prompts of the CLI:

.. code-block:: text

    ============================= SomeDL - New output template ============================= 

    Utility to automatically move/copy your current library to a new storage template.
    You can also sort songs downloaded with SomeDL from another folder into your music library.
    This tool assumes it is used on files with complete metadata, it does not change metadata.
    If you want to organize a library with incomplete metadata, use 'somedl import' instead.

    This tool is in beta! Always back up your files first, especially when using Move mode.
    If you want you can share your feedback on this tool (positive or negative) on: 
    https://github.com/ChemistryGull/SomeDL/discussions


        1/4 | Source folder
            | Your old music library folder, or the folder containing the files you want to sort into your library
            |  Path > /home/USER/Music/Old_SomeDL_Folder/

        2/4 | Destination folder
            | Your new music library folder
            |  Path > /home/USER/Music/SomeDL/

        3/4 | NEW output template
            | Available placeholders: {song} and ({artist} or {album_artist})
            | Optional Placeholders: {album}, {year}, {track_pos}, {track_count}
            | Example: {album_artist}/{year} - {album}/{track_pos} - {song}
            | or       {album_artist}/{album}/{artist} - {song}
            | or       {album_artist}/{artist} - {song}
            | or others
            |  New output template > {album_artist}/{year} - {album}/{track_pos} - {song}

        4/4 | Mode
            | Copy - original files are left in place (Recommended unless you have a backup and know what you are doing)
            | Move - original files are deleted after import
            |  [copy/move] > copy



How can I add metadata to already downloaded files?
---------------------------------------------------

If you already have a library of songs downloaded with yt-dlp or other downloaders, you can use the ``somedl import`` utility. 
It will ask you to provide the path to your files and the path to a new folder, or your SomeDL library. 
You will also have to provide the new output template and what import mode you want to choose.

Import modes are:

- copy: Original files are left in place (recommended unless you have a backup and know what you are doing)
- move: original files are deleted after import
- update: Just update the metadata of the original files. This will neither change the filename nor move the file, but change the original file metadata itself. Use copy instead if you want to keep the original files.

Then you will have to choose the mode of metadata detection. SomeDL has to figure out what each song is. There are different strategies to do so:

A) YouTube video ID in the filename (e.g. ``The Cold [xI91NneSY5Y].mp3``)
B) "Artist - Song" file naming scheme
C) Inferring from existing metadata

Choose the mode that fits best for your usecase. Do you have many songs downloaded with yt-dlp and still have the 11-digit Video ID [xI91NneSY5Y]? Type yes for option A. 
Do all your files follow a "Artist - Song" file naming scheme? Type yes for option B. 
Do you know your files have valid metadata (only Artist name and Song name are needed)? 
Choose option C. You can also combine options, like A and C or A and B. You cannot combine B with C.

After that, you can start with the import. It is best to first test the import on a smaller folder.

Below you can see the interactive prompts of the CLI:

.. code-block:: text

    ================================== SomeDL - Import ================================== 

    Import music files from any folder into your configured folder structure.
    It will update the metadata in your files in the same way as downloading with SomeDL would.
    Supported file extentions: mp3, m4a, ogg, opus, flac

    This tool is in beta! Always back up your files first, especially when using Move mode.
    If you want you can share your feedback on this tool (positive or negative) on: https://github.com/ChemistryGull/SomeDL/discussions

    1/6 | Source folder
        | Folder containing the music files to import.
        | Leave empty to use the current directory: /home/USER
        |  Path > /home/USER/Music/random_downloads/

    2/6 | Destination folder
        | Where imported files will be placed.
        | Can be a new folder or the folder with your SomeDL downloaded library.
        | Can not be the same folder as the source folder!
        | Leave empty for default folder: /home/USER/Music/SomeDL
        | Ignore if you only want to update the metadata of the original files, without moving them.
        |  Path > /home/USER/Music/SomeDL/

    3/6 | Output template
        | Controls how imported files are named and organised.
        | Leave empty to use the configured default: {album_artist}/{album_artist} - {song}
        | Ignore if you only want to update the metadata of the original files, without moving them.
        | Available placeholders: {song} and ({artist} or {album_artist})
        | Optional Placeholders: {album}, {year}, {track_pos}, {track_count}
        | Example: {album_artist}/{year} - {album}/{track_pos} - {song}
        | or       {album_artist}/{album}/{artist} - {song}
        | or       {album_artist}/{artist} - {song}
        | or others
        |  New output template > {album_artist}/{album}/{artist} - {song}

    4/6 | Import music files recursively?
        | Should files inside subfolders also be imported?
        |  [Y/n] > Y

    5/6 | Import mode
        | Copy - original files are left in place (Recommended unless you have a backup and know what you are doing)
        | Move - original files are deleted after import
        | Update - Just update the metadata of the original files. This will neither change the filename nor move the files.
        |  [copy/move/update] > copy

    6/6 | Metadata detection
        | SomeDL needs to identify each song to update its metadata.
        | There are several strategies to do so:
        | A: Video ID in filename, B: artist and title info in filename or C: metadata.
        | Strategy A can be mixed with B or C as fallback. If B is used C cannot be used.
        | Please add information to your files:
        | 
        | A) Do some of your files contain the YouTube video ID in square brackets?
        |    This is often the case if your songs were downloaded with yt-dlp
        |    e.g. The Cold [xI91NneSY5Y].mp3
        |    Answer Yes if at least some files match.
        |     [Y/n] > Y
        | 
        | B) Do ALL your filenames follow a "Artist - Song" scheme or similar?
        |    YouTube search will be used to fetch metadata.
        |    e.g.  Delain - The cold.mp3
        |    or    Hideaway Paradise by Delain.mp3
        |    The filename must contain the artist name and the song name.
        |    !!! Only put Yes if this is the case for every music file in the import folder.
        |     [y/N] > N
        | 
        | C) Should SomeDL identify songs from metadata already embedded in the files?
        |     [Y/n] > Y




How can I update only specific metadata for my already downloaded songs?
-------------------------------------------------------------------------

If you want to update synced or plain lyrics in your library, you can use ``somedl update-metadata``. There are two modes: a "add" mode to only add missing data, and an "update" mode to update metadata even if it's already present. A few things to consider:

* So far, only synced and plain lyrics can be updated with this tool.
* This utility has had little testing, so please test it on a small amount of disposable files before using it on your whole library!
* The settings in your config file must reflect the update that you want to make. For example, if you want to add or update synced lyrics but have disabled synced lyrics in the config, this won't work.

.. code-block:: text

    ============================= SomeDL - Update Metadata ============================= 

    Utility to update or redownload missing metadata. Currently only supports updating lyrics

    ATTENTION: I've done little testing with this utility, please test it on a small amount of disposable files first!!
    ATTENTION: The settings in your config file must reflect the update that you want to make
                e.g. if you want to add or update synced lyrics, but have disabled synced lyrics in the config, this won't work.
    If you want you can share your feedback on this tool (positive or negative) on: https://github.com/ChemistryGull/SomeDL/discussions


    1/3 | Source folder
        | Your old music library folder, or the folder containing the files you want to sort into your library
        |  Path > /home/USER/Music/SomeDL/

    2/3 | Mode
        | Add - Only add missing data
        | Update - Update all data, even if already present
        |  [add/update] > add

    3/3 | What to update
        | 
        | 1) Plain Lyrics
        |  [y/n] > y
        | 
        | 2) Synced Lyrics
        |  [y/n] > y

