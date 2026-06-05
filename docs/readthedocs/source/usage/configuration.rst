Configuring SomeDL
==================

You can either edit the configuration file directly, or use the WebUI's Settings tab to change configurations.

Configuration file
------------------

SomeDL comes with a `somedl_config.toml` configuration file. To generate this file, or regenerate it with default configurations, run:

.. code-block:: bash

    somedl --generate-config

The config file is usually located at:

=======     =====  
Linux       ``~/.config/SomeDL/somedl_config.toml``
Windows     ``C:\Users\<User>\AppData\Roaming\SomeDL\somedl_config.toml``    
MacOS       ``~/Library/Application Support/SomeDL/somedl_config.toml``    
=======     =====

In the config file you can edit the behaviour of SomeDL, like defining an output template, setting default output format & output folder and much more.
Inside this config file, there are comments that explain each setting.
(For Windows users it is recommended to read and edit the config file with an editor that has syntax highlighing, like Notepad++).

Configuration from the WebUI
----------------------------

All configuration changes can also be made directly form the WebUI's Settings tab. Click apply after making changes to the configurations.
A few settings require a complete restart of the application (e.g. number of concurrent downloaders).
Please restart the application if there are problems.
