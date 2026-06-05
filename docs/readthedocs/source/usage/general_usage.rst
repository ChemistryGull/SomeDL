General usage
=============

CLI
---
Simply type ``somedl`` followed by your search query in quotes into the terminal (CMD or PowerShell on Windows).

.. code-block:: bash

    somedl "Nirvana - Smells like teen spirit"

You can also search by:

* YouTube or YouTube Music URL
* YouTube Playlist URL 
* YouTube Album URL
* YouTube Artist URL

Search for multiple songs at once by seperating them with spaces.

.. code-block:: bash

    somedl "https://music.youtube.com/watch?v=W0Wo5zhgvpM" "https://music.youtube.com/playlist?list=OLAK5uy_mHURRD4wyePH5Kl8wQkgyfFhbvmK2pYk4" "Iron maiden - run to the hills"

Run somedl -h to get more information for the different configuration options.


WebUI
-----

To start the WebUI, run the following command:

.. code-block:: bash

    somedl web

A browser window will open. The default address is ``http://127.0.0.1:5000/``.
To stop the WebUI, press ``Ctrl+C`` in the terminal or click the shutdown button in the WebUI.