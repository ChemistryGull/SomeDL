Requirements
============


Python (required)
-----------------

Python 3.10 or newer is required. Visit `How to install python <https://github.com/ChemistryGull/SomeDL/blob/main/docs/how_to_install_python.md>`_ for a short guide.


FFmpeg (required)
-----------------

SomeDL uses yt-dlp, which needs `ffmpeg <https://ffmpeg.org/>`_ in order to convert the downloaded audio file to mp3.
On Windows, the fastest way to install ffmpeg is by using winget: 

.. code-block:: bash

    winget install ffmpeg

Visit `How to install ffmpeg <https://github.com/ChemistryGull/SomeDL/blob/main/docs/how_to_install_ffmpeg.md>`_ for a manual installation or if the winget installation fails.

Deno (recommended)
------------------

It is also recommended to have Deno installed. 
Yt-dlp needs deno to work properly (`More info <https://github.com/yt-dlp/yt-dlp/wiki/EJS>`_). 
To install Deno, follow the guide on the `Deno website <https://docs.deno.com/runtime/getting_started/installation/>`_.
