grace-dizmo
===========

Install
-------

Installing grace-dizmo can be done the same way as **Grace** (https://github.com/mdiener/grace). You do not need to install **Grace** first, as it will be automatically installed as a dependency.

When installing grace-dizmo, there are two options for a skeleton. Either _default_ or _joose_. For more information please see: https://www.github.com/mdiener/grace-dizmo-skeleton.

License
-------

Grace is released under a GPL license. You can read the full license in the attached LICENSE.txt file.

General
-------

**Grace** can also be conveniently used to build and manage dizmos. It allows you to create dizmos, takes care of the plist file for you (you only have to worry about the keys you actually want to adjust, except the mandatory bundle). All commands except help and clean can be used with dizmo as a modifier.
Upon building a new dizmo, there will be a special config file placed in your project directory. It contains only _bundle_ as a key, which represents the bundle your dizmo belongs to. You can then add any other key dizmo supports in that file, and it will be placed into your Info.plist upon building of the dizmo.

**The config file provided needs to include the version of your project, otherwise the building of a dizmo will fail**.

Dizmo
-----

The first module provided is for dizmo development. Just specify _dizmo_ when creating a new project as the plugin.

The dizmo plugin adds additional config options in the project.cfg file. The following is a list of adjustable options:
* development_region: The region you develop your dizmo.
* display_name: The name that is being displayed in your dizmo (title attribute)
* bundle_identifier: Identifier of your dizmo, used for storing and grouping dizmos together.
* width: The initial width of your dizmo.
* height: The initial height of your dizmo.

The following options should not be changed, unless you exactly know what you are doing.
* box_inset_x
* box_inset_y
* api_version
* main_html
* urls

The special key *credentials* can be used to supply credentials to log in to the store and upload/publish/unpublish the dizmo. These keys can also be supplied through the global configuration file.
* credentials
  * username: If left empty, grace will ask for it on executing the upload/publish/unpublish command
  * password: If left empty, grace will ask for it on executing the upload/publish/unpublish command
