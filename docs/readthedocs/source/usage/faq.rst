FAQ
===

How can I give feedback or make feature requests?
-------------------------------------------------

- **Bug report**: Open an issue at https://github.com/ChemistryGull/SomeDL/issues
- **Feature requests**: Open an issue or start a discussion in the
  ideas category: https://github.com/ChemistryGull/SomeDL/discussions/categories/ideas
- **General feedback**: Start a discussion in the Feedback category:
  https://github.com/ChemistryGull/SomeDL/discussions/categories/feedback
- **General question**: Read the FAQ or ask in the Q&A category:
  https://github.com/ChemistryGull/SomeDL/discussions/categories/q-a
- **Anything else**: Start a discussion in the general category:
  https://github.com/ChemistryGull/SomeDL/discussions/categories/general


Why should I use SomeDL over yt-dlp?
------------------------------------

yt-dlp has the ability to add metadata and thumbnails with the flags
``--embed-metadata`` and ``--embed-thumbnail``. However, this data is incomplete
and often messy. Examples:

- No genre data (it sets "Music" as the genre)
- Embeds rectangular thumbnail instead of square cover art
- Does not include lyrics
- Often treats songs as singles, even if they are part of an album (leading to
  wrong album name and thumbnail)
- Wrong date (often uses upload date instead of release date)
- No track numbers

Yt-dlp is not a full music metadata downloading tool (and does not claim to be).
That is why SomeDL uses multiple sources to get more accurate metadata.
Yt-dlp is still the backbone of SomeDL and it would not exist without it.
When using SomeDL, you are still using yt-dlp under the hood, just with the additional benefits that SomeDL provides.


Why is the wrong version of the song downloaded?
------------------------------------------------

Rarely, a "radio version" or similar upload has more views than the original,
so it appears first in YouTube's search results and is therefore selected by SomeDL.

Possible ways to get the correct version:

- Add terms like "Original" to the search query, e.g.
  "Nirvana - Smells Like Teen Spirit original"
- Search for the song on YouTube Music and download via URL
- Download it directly via the WebUI YouTube Search

IMPORTANT: Always use the link of the original soundtrack. Do not use the music
video version, because it may not have the correct metadata and audio track,
causing SomeDL to search again and potentially produce the same issue.

If you do not use a proper YouTube Music URL, you are always dependent on the
YouTube search algorithm. However, it is accurate in over 95% of cases.


Why does downloading pause at "Fetching lyrics from lrclib" for so long?
-------------------------------------------------------------------------

Lrclib is a free crowdsourced lyrics API that is widely used. During peak usage,
it may become slow.

If you do not need synced lyrics, you can switch the lyrics provider to YouTube
in the SomeDL config file.


Why is the wrong genre / no genre set?
--------------------------------------

SomeDL gets genre information from MusicBrainz (neither YouTube nor Genius
provide genre data via their APIs).

MusicBrainz genre data is crowdsourced, so:

- Some artists have no genre set
- Some have incorrect genres

Anyone can create an account on MusicBrainz and add or vote for genre
tags. Contributions are encouraged.

*Genre information is applied per artist, meaning all songs by the same artist
share the same genre. MusicBrainz does have album- and track-level tags, but
they are often incomplete, so artist-level tags are preferred.*




What is the "Download Report .... .html" file?
----------------------------------------------

For every download of more than one song, a download report is created. You can
open it in any browser. It provides an overview of the downloaded metadata and
helps verify whether anything is incorrect. To disable the download report, run ``somedl --disable-report``


How long does a song download take?
------------------------------------

Usually around 3-4 seconds per song when downloading a list of 10+ songs with
default concurrency.

Downloading a single song takes about 8-10 seconds.

Increasing concurrency can reduce this to about 2 seconds per song, but this
may cause rate limiting or temporary blocking by YouTube if overused.


What does this error message / warning mean?
--------------------------------------------

.. code-block:: text

    WARNING - Video has no song ID - this might be a regular YouTube video, not a song.

This means the video is not registered as a song on YouTube. This is common for
regular videos. In some cases it may be a small creator or fan upload, where
metadata must be added manually after downloading with yt-dlp.


YT-DLP specific warnings:
-------------------------

.. code-block:: text

    WARNING - >_yt-dlp: [youtube] No supported JavaScript runtime could be found.
    Only deno is enabled by default; to use another runtime add –js-runtimes RUNTIME[:PATH]
    YouTube extraction without a JS runtime has been deprecated.

This usually means Deno is not installed correctly. See:
https://github.com/ChemistryGull/SomeDL#deno


.. code-block:: text

    WARNING - >_yt-dlp: [youtube] ... Some android_vr client https formats have been skipped

YouTube is experimenting with streaming formats. This may result in fallback
to video download + audio extraction. File sizes may be larger, but downloads
still work normally.


.. code-block:: text

    ERROR - >_yt-dlp: Did not get any data blocks

Usually related to the above warning. yt-dlp typically recovers automatically.


.. code-block:: text

    WARNING - >_yt-dlp: JS Challenge Provider "deno" returned an invalid response

Caused by changes in YouTube's anti-bot system. Updating yt-dlp usually fixes
this.


.. code-block:: text

    ERROR - >_yt-dlp: Sign in to confirm your age

This is an age-restricted video. Use cookies authentication as described in:
https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp

See also:
https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies

If this occurs, the download will fail unless authentication is provided.