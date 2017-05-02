from __future__ import print_function
from builtins import next
from builtins import input
from builtins import str
import os
import plistlib
from shutil import move, rmtree, copy
import sys
from grace.error import MissingKeyError, WrongFormatError, FileNotWritableError, RemoveFolderError, UnknownCommandError, WrongLoginCredentials, RemoteServerError, KeyNotAllowedError, FileNotFoundError
import grace.create
import grace.build
import grace.testit
import grace.zipit
import grace.deploy
import grace.lint
import grace.config
from grace.utils import update, load_json, write_json, isstring
import requests
import getpass
from copy import deepcopy
import hashlib
import zipfile
import re


requests.packages.urllib3.disable_warnings()


def _escapeAndEncode(text):
    m = plistlib._controlCharPat.search(text)
    if m is not None:
        raise ValueError("strings can't contains control characters; "
                         "use plistlib.Data instead")
    text = text.replace("\r\n", "\n")       # convert DOS line endings
    text = text.replace("\r", "\n")         # convert Mac line endings
    text = text.replace("&", "&amp;")       # escape '&'
    text = text.replace("<", "&lt;")        # escape '<'
    text = text.replace(">", "&gt;")        # escape '>'

    return text


def writeDict(self, d):
    self.beginElement("dict")
    items = d.items()
    for key, value in items:
        if not isstring(key):
            raise TypeError("keys must be strings")
        self.simpleElement("key", key)
        self.writeValue(value)
    self.endElement("dict")


if sys.version_info.major < 3:
    plistlib._escapeAndEncode = _escapeAndEncode
    plistlib.PlistWriter.writeDict = writeDict


def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")


def get_path():
    if we_are_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


def get_plist(config, testname=None, test=False):
    embedded_bundles = []

    if test:
        display_name = config['dizmo_settings']['display_name'] + ' ' + testname
        identifier = config['dizmo_settings']['bundle_identifier'] + '.' + testname.lower()
    else:
        display_name = config['dizmo_settings']['display_name']
        identifier = config['dizmo_settings']['bundle_identifier']

        for index, project in enumerate(config['embedded_projects']):
            embedded_bundles.append(project['bundle_identifier'])

    plist = dict(
        BundleDisplayName=display_name,
        BundleIdentifier=identifier,
        BundleName=config['dizmo_settings']['bundle_name'],
        BundleShortVersionString=config['version'],
        BundleVersion=config['version'],
        CloseBoxInsetX=config['dizmo_settings']['box_inset_x'],
        CloseBoxInsetY=config['dizmo_settings']['box_inset_y'],
        MainHTML=config['dizmo_settings']['main_html'],
        Width=config['dizmo_settings']['width'],
        Height=config['dizmo_settings']['height'],
        ApiVersion=config['dizmo_settings']['api_version'],
        ElementsVersion=config['dizmo_settings']['elements_version'],
        Description=config['dizmo_settings']['description'],
        ChangeLog=config['dizmo_settings']['change_log'],
        MinSpaceVersion=config['dizmo_settings']['min_space_version'],
        Tags=config['dizmo_settings']['tags'],
        Category=config['dizmo_settings']['category'],
        HiddenDizmo=config['dizmo_settings']['hidden_dizmo'],
        AllowResize=config['dizmo_settings']['allow_resize'],
        TitleEditable=config['dizmo_settings']['title_editable'],
        ForceUpdate=config['dizmo_settings']['force_update']
    )

    if 'additional_plist_values' in config['dizmo_settings']:
        keys = config['dizmo_settings']['additional_plist_values']
        for key, value in keys.items():
            plist[key] = value

    if config['dizmo_settings']['helper_version'] is not None:
        plist['HelperVersion'] = config['dizmo_settings']['helper_version']

    if config['dizmo_settings']['elements_version'] is not None:
        plist['ElementsVersion'] = config['dizmo_settings']['elements_version']

    if config['dizmo_settings']['tree_values'] is not None:
        if config['dizmo_settings']['tree_values']['attributes'] is not None:
            plist['Attributes'] = config['dizmo_settings']['tree_values']['attributes']

        if config['dizmo_settings']['tree_values']['private'] is not None:
            plist['Private'] = config['dizmo_settings']['tree_values']['private']

        if config['dizmo_settings']['tree_values']['public'] is not None:
            plist['Public'] = config['dizmo_settings']['tree_values']['public']

    if len(embedded_bundles) != 0:
        plist['EmbeddedBundles'] = embedded_bundles

    return plist


def get_skeleton_names():
    return ['basic', 'joose', 'coffee']


class CommandLineParser(grace.cmdparse.CommandLineParser):
    def _get_epilog(self):
        epilog = super(CommandLineParser, self)._get_epilog()

        return epilog + '''\

Grace Dizmo
-----------
Grace-dizmo is the currently loaded plugin for this project.
It allows development of dizmos through various helper functions built in grace.
Grace-dizmo also provides three new functions that are solely used to
publish and unpublish a dizmo.

Additional Task Commands
------------------------
publish         Publish an uploaded dizmo and make it publicly available.
publish:display Display the publish status of a dizmo.
unpublish       Remove a dizmo's publish status and make it unavailable in the store.

Additional Overwrite Commands
-----------------------------
dizmo_settings:width
dizmo_settings:height
dizmo_settings:allow_resize
dizmo_settings:title_editable

Further Reading
---------------
For more information visit: https://www.github.com/mdiener/grace-dizmo
'''


class Config(grace.config.Config):
    def __init__(self):
        super(Config, self).__init__()

        self._categories = [
            'books_and_references',
            'comics',
            'communication',
            'education',
            'entertainment',
            'finance',
            'games',
            'health_and_fitness',
            'libraries_and_demo',
            'lifestyle',
            'media_and_video',
            'medical',
            'music_and_audio',
            'news_and_magazines',
            'personalization',
            'photography',
            'productivity',
            'shopping',
            'social',
            'sports',
            'tools',
            'transportation',
            'travel_and_local',
            'weather'
        ]

    def _check_update_keys(self, updates):
        if 'dizmo_settings' in updates:
            dizmo_settings = updates['dizmo_settings']

            if ('bundle_name' in dizmo_settings or
                    'bundle_identifier' in dizmo_settings or
                    'box_inset_x' in dizmo_settings or
                    'box_inset_y' in dizmo_settings or
                    'description' in dizmo_settings or
                    'tags' in dizmo_settings or
                    'category' in dizmo_settings or
                    'min_space_version' in dizmo_settings or
                    'change_log' in dizmo_settings or
                    'api_version' in dizmo_settings or
                    'main_html' in dizmo_settings or
                    'hidden_dizmo' in dizmo_settings or
                    'force_update' in dizmo_settings or
                    'elements_version' in dizmo_settings):

                raise KeyNotAllowedError('Only "width", "height", "allow_resize" and "title_editable" are allowed under "dizmo_settings".')

            if 'bundle_identifier_subproject' in dizmo_settings:
                updates['dizmo_settings']['bundle_identifier'] = dizmo_settings['bundle_identifier_subproject']
                updates['dizmo_settings'].pop('bundle_identifier_subproject')

        super(Config, self)._check_update_keys(updates)

    def _parse_subprojects(self):
        super(Config, self)._parse_subprojects()

        for index, project in enumerate(self._config['embedded_projects']):
            if 'bundle_identifier' not in project:
                raise MissingKeyError('The bundle_identifier of the embedded project has not been set.')

    def _preparse_config(self, config):
        if 'dizmo_settings' in config:
            if 'urls' in config['dizmo_settings']:
                if 'dizmo_store' in config['dizmo_settings']['urls']:
                    if 'urls' in config:
                        config['urls']['dizmo_store'] = config['dizmo_settings']['urls']['dizmo_store']
                    else:
                        config['urls'] = {
                            'dizmo_store': config['dizmo_settings']['urls']['dizmo_store']
                        }

                    config['dizmo_settings'].pop('urls')

            username = None
            password = None
            if 'credentials' in config['dizmo_settings']:
                if 'username' in config['dizmo_settings']['credentials']:
                    username = config['dizmo_settings']['credentials']['username']
                if 'password' in config['dizmo_settings']['credentials']:
                    password = config['dizmo_settings']['credentials']['password']

            if username is not None or password is not None:
                if 'credentials' not in config:
                    config['credentials'] = {}
                if username is not None:
                    config['credentials']['username'] = username
                if password is not None:
                    config['credentials']['password'] = password

        return config

    def _parse_config(self):
        super(Config, self)._parse_config()

        if 'dizmo_settings' not in self._config:
            raise MissingKeyError('Could not find settings for dizmo.')

        self._dizmo_config = self._config['dizmo_settings']

        if 'display_name' not in self._dizmo_config:
            raise MissingKeyError('Specify a display name in your config file under `dizmo_settings`.')
        else:
            if not isstring(self._dizmo_config['display_name']):
                raise WrongFormatError('The display_name key needs to be a string.')
            else:
                if len(self._dizmo_config['display_name']) == 0:
                    raise WrongFormatError('The display_name has to consist of at least one character.')

        if 'bundle_name' not in self._dizmo_config:
            raise MissingKeyError('Please specify a "bundle_name" under the dizmo_settings key in your project.cfg file.')
        else:
            if not isstring(self._dizmo_config['bundle_name']):
                raise WrongFormatError('The bundle_name key needs to be a string.')
            else:
                if len(self._dizmo_config['bundle_name']) == 0:
                    raise WrongFormatError('The bundle_name needs to be at least one character long.')

        if 'bundle_identifier' not in self._dizmo_config:
            raise MissingKeyError('Specify a bundle identifier in your config file under `dizmo_settings`.')
        else:
            if not isstring(self._dizmo_config['bundle_identifier']):
                raise WrongFormatError('The bundle_identifier key needs to be a string.')
            else:
                if len(self._dizmo_config['bundle_identifier']) == 0:
                    raise WrongFormatError('The bundle_identifier has to consist of at least one character.')

        if 'width' not in self._dizmo_config:
            raise MissingKeyError('Specify a width in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['width'], int):
                raise WrongFormatError('The width key needs to be a number.')

        if 'height' not in self._dizmo_config:
            raise MissingKeyError('Specify a height in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['height'], int):
                raise WrongFormatError('The height key needs to be a number.')

        if 'box_inset_x' not in self._dizmo_config:
            raise MissingKeyError('Specify a box inset x in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['box_inset_x'], int):
                raise WrongFormatError('The box_inset_x key needs to be a number.')

        if 'box_inset_y' not in self._dizmo_config:
            raise MissingKeyError('Specify a box inset y in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['box_inset_y'], int):
                raise WrongFormatError('The box_inset_y key needs to be a number.')

        if 'description' not in self._dizmo_config:
            raise MissingKeyError('Add a description in your config file under `dizmo_settings`.')
        else:
            if not isstring(self._dizmo_config['description']):
                raise WrongFormatError('The description needs to be a string.')
            else:
                if len(self._dizmo_config['description']) == 0:
                    raise WrongFormatError('The description has to consist of at least one character.')

        if 'tags' not in self._dizmo_config:
            raise MissingKeyError('Add a list of tags in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['tags'], list):
                raise WrongFormatError('The tags need to be a list ["...", "..."].')

        if 'category' not in self._dizmo_config:
            raise MissingKeyError('Add a category in your config file under `dizmo_settings`.')
        else:
            if not isstring(self._dizmo_config['category']):
                raise WrongFormatError('The category needs to be a string.')
            else:
                if len(self._dizmo_config['category']) == 0:
                    raise WrongFormatError('The category has to consist of at least one character.')
                if self._dizmo_config['category'] not in self._categories:
                    raise WrongFormatError('The category has to be one of the following: "books_and_references", "comics", "communication", "education", "entertainment", "finance", "games", "health_and_fitness", "libraries_and_demo", "lifestyle", "media_and_video", "medical", "music_and_audio", "news_and_magazines", "personalization", "photography", "productivity", "shopping", "social", "sports", "tools", "transportation", "travel_and_local", "weather"')

        if 'min_space_version' not in self._dizmo_config:
            raise MissingKeyError('Add a min_space_version in your config file under `dizmo_settings`.')
        else:
            if not isstring(self._dizmo_config['min_space_version']):
                raise WrongFormatError('The min_space_version needs to be string.')
            else:
                if len(self._dizmo_config['min_space_version']) == 0:
                    raise WrongFormatError('The min_space_version has to consist of at least one character.')

        if 'change_log' not in self._dizmo_config:
            raise MissingKeyError('Add a change_log in your config file under `dizmo_settings`.')
        else:
            if not isstring(self._dizmo_config['change_log']):
                raise WrongFormatError('The change_log needs to be string.')
            else:
                if len(self._dizmo_config['change_log']) == 0:
                    raise WrongFormatError('The change_log has to consist of at least one character.')

        if 'api_version' not in self._dizmo_config:
            raise MissingKeyError('Specify an api version in your config file under `dizmo_settings`.')
        else:
            if not isstring(self._dizmo_config['api_version']):
                raise WrongFormatError('The api_version key needs to be a string.')
            else:
                if len(self._dizmo_config['api_version']) == 0:
                    raise WrongFormatError('The api_version has to consist of at least one character.')

        if 'main_html' not in self._dizmo_config:
            raise MissingKeyError('Specify a main html in your config file under `dizmo_settings`.')
        else:
            if not isstring(self._dizmo_config['main_html']):
                raise WrongFormatError('The main_html key needs to be a string.')
            else:
                if len(self._dizmo_config['main_html']) == 0:
                    raise WrongFormatError('The main_html has to consist of at least one character.')

        if 'hidden_dizmo' not in self._dizmo_config:
            self._config['dizmo_settings']['hidden_dizmo'] = False
        else:
            if not isinstance(self._dizmo_config['hidden_dizmo'], bool):
                raise WrongFormatError('The provided value for hidden_dizmo needs to be a boolean.')

        if 'allow_resize' not in self._dizmo_config:
            self._config['dizmo_settings']['allow_resize'] = False
        else:
            if not isinstance(self._dizmo_config['allow_resize'], bool):
                raise WrongFormatError('The provided value for allow_resize needs to be a boolean')

        if 'title_editable' not in self._dizmo_config:
            self._config['dizmo_settings']['title_editable'] = True
        else:
            if not isinstance(self._dizmo_config['title_editable'], bool):
                raise WrongFormatError('The provided value for title_editable needs to be a boolean.')

        if 'force_update' not in self._dizmo_config:
            self._config['dizmo_settings']['force_update'] = False
        else:
            if not isinstance(self._dizmo_config['force_update'], bool):
                raise WrongFormatError('The provided value for force_update needs to be a boolean.')

        if 'elements_version' not in self._dizmo_config:
            self._config['dizmo_settings']['elements_version'] = None

        if 'helper_version' not in self._dizmo_config:
            self._config['dizmo_settings']['helper_version'] = None

        if 'attributes' not in self._dizmo_config:
            self._config['dizmo_settings']['attributes'] = {}

        if 'private' not in self._dizmo_config:
            self._config['dizmo_settings']['private'] = {}

        if 'public' not in self._dizmo_config:
            self._config['dizmo_settings']['public'] = {}

        if 'tree_values' not in self._dizmo_config:
            self._config['dizmo_settings']['tree_values'] = None
        else:
            if not isinstance(self._dizmo_config['tree_values'], dict):
                raise WrongFormatError('The provided tree_values key has to be an object.')

            if 'attributes' not in self._dizmo_config['tree_values']:
                self._config['dizmo_settings']['tree_values']['attributes'] = None
            else:
                if not isinstance(self._dizmo_config['tree_values']['attributes'], dict):
                    raise WrongFormatError('The provided attributes key in tree_values has to be an object.')

            if 'private' not in self._dizmo_config['tree_values']:
                self._config['dizmo_settings']['tree_values']['private'] = None
            else:
                if not isinstance(self._dizmo_config['tree_values']['private'], dict):
                    raise WrongFormatError('The provided private key in tree_values has to be an object.')

            if 'public' not in self._dizmo_config['tree_values']:
                self._config['dizmo_settings']['tree_values']['public'] = None
            else:
                if not isinstance(self._dizmo_config['tree_values']['public'], dict):
                    raise WrongFormatError('The provided public key in tree_values has to be an object.')


class New(grace.create.New):
    def __init__(self, projectName, skeleton):
        self._projectName = projectName
        self._root = get_path()
        self._cwd = os.getcwd()

        self._skeleton_parent_folder = os.path.join(os.path.expanduser('~'), '.grace', 'skeletons', 'custom')
        self._skeleton_path = os.path.join(os.path.expanduser('~'), '.grace', 'skeletons', 'custom', hashlib.md5(skeleton.encode(sys.getfilesystemencoding())).hexdigest())
        self._skeleton_url = skeleton

        if skeleton == 'basic':
            self._skeleton_url = 'https://github.com/dizmo/grace-dizmo-skeleton/archive/basic.zip'
            self._skeleton_parent_folder = os.path.join(os.path.expanduser('~'), '.grace', 'skeletons', 'grace-dizmo')
            self._skeleton_path = os.path.join(self._skeleton_parent_folder, 'basic')
        if skeleton == 'joose':
            self._skeleton_url = 'https://github.com/dizmo/grace-dizmo-skeleton/archive/joose.zip'
            self._skeleton_parent_folder = os.path.join(os.path.expanduser('~'), '.grace', 'skeletons', 'grace-dizmo')
            self._skeleton_path = os.path.join(self._skeleton_parent_folder, 'joose')
        if skeleton == 'coffee':
            self._skeleton_url = 'https://github.com/dizmo/grace-dizmo-skeleton/archive/coffee.zip'
            self._skeleton_parent_folder = os.path.join(os.path.expanduser('~'), '.grace', 'skeletons', 'grace-dizmo')
            self._skeleton_path = os.path.join(self._skeleton_parent_folder, 'coffee')
        if skeleton == 'transcrypt':
            self._skeleton_url = 'https://github.com/dizmo/grace-dizmo-skeleton/archive/transcrypt.zip'
            self._skeleton_parent_folder = os.path.join(os.path.expanduser('~'), '.grace', 'skeletons', 'grace-dizmo')
            self._skeleton_path = os.path.join(self._skeleton_parent_folder, 'transcrypt')

        self._download_skeleton()

        self._projectPath = os.path.join(self._cwd, self._projectName)

        self._copy_structure()
        self._replace_strings()


class Build(grace.build.Build):
    def __init__(self, config):
        super(Build, self).__init__(config)

    def run(self):
        help_path = os.path.join(os.getcwd(), 'help')
        path = self._config['build_path']

        super(Build, self).run()

        self._copy_images(path)
        self._build_help(help_path)

        plist = get_plist(self._config)
        try:
            plistlib.writePlist(plist, os.path.join(path, 'Info.plist'))
        except:
            raise
            # raise FileNotWritableError('Could not write plist to target location: ', path)

    def _copy_images(self, build_path):
        assets_path = os.path.join(build_path, 'assets')

        image_PNG_source = os.path.join(os.getcwd(), 'Icon.png')
        if not os.path.isfile(image_PNG_source):
            image_PNG_source = os.path.join(assets_path, 'Icon.png')

        image_PNG_dark_source = os.path.join(os.getcwd(), 'Icon-dark.png')
        if not os.path.isfile(image_PNG_dark_source):
            image_PNG_dark_source = os.path.join(assets_path, 'Icon-dark.png')

        image_SVG_source = os.path.join(os.getcwd(), 'Icon.svg')
        if not os.path.isfile(image_SVG_source):
            image_SVG_source = os.path.join(assets_path, 'Icon.svg')

        image_SVG_dark_source = os.path.join(os.getcwd(), 'Icon-dark.svg')
        if not os.path.isfile(image_SVG_dark_source):
            image_SVG_dark_source = os.path.join(assets_path, 'Icon-dark.svg')

        image_preview_source = os.path.join(os.getcwd(), 'Preview.png')
        if not os.path.isfile(image_preview_source):
            image_preview_source = os.path.join(assets_path, 'Preview.png')

        if os.path.isfile(image_PNG_source):
            try:
                copy(image_PNG_source, os.path.join(build_path, 'Icon.png'))
            except:
                print('Could not copy your Icon.png file.')

        if os.path.isfile(image_PNG_dark_source):
            try:
                copy(image_PNG_dark_source, os.path.join(build_path, 'Icon-dark.png'))
            except:
                print('Could not copy your Icon-dark.png file.')

        if os.path.isfile(image_SVG_source):
            try:
                copy(image_SVG_source, os.path.join(build_path, 'Icon.svg'))
            except:
                print('Could not copy your Icon.svg file.')

        if os.path.isfile(image_SVG_dark_source):
            try:
                copy(image_SVG_dark_source, os.path.join(build_path, 'Icon-dark.svg'))
            except:
                print('Could not copy your Icon-dark.svg file.')

        if os.path.isfile(image_preview_source):
            try:
                copy(image_preview_source, os.path.join(build_path, 'Preview.png'))
            except:
                print('Could not copy your Preview.png file.')

    def _build_help(self, help_path):
        valid = False

        if not os.path.exists(help_path):
            print('There is no help folder. Please refer to the dizmo documentation on how to create one.')
            return

        language_dirs = next(os.walk(help_path))[1]

        for lang_dir in language_dirs:
            if len(lang_dir) <= 2:
                if os.path.isfile(os.path.join(help_path, lang_dir, 'help.md')):
                    valid = True

        if not valid:
            print('Could not find any help.md file in any language directory under help. Please refer to the dizmo documentation for more information about how to set up the help directory.')
            return

        z = None
        destination = os.path.join(os.getcwd(), self._config['build_path'], 'help.zip')

        try:
            z = zipfile.ZipFile(destination, 'a', zipfile.ZIP_DEFLATED)
        except RuntimeError as e:
            z = zipfile.ZipFile(destination, 'a')

        for root, dirs, files in os.walk(help_path):
            for f in files:
                tmpfilename = os.path.join(root, f).split(help_path)[1][1:]
                zipfilename = os.path.join('help', tmpfilename)
                try:
                    z.write(os.path.join(root, f), zipfilename)
                except:
                    raise FileNotWritableError('Could not write to the zip file.')


class Test(grace.testit.Test):
    def __init__(self, config):
        super(Test, self).__init__(config)

    def run(self, testname):
        super(Test, self).run(testname)

        plist = get_plist(self._config, testname, test=True)
        path = os.path.join(os.getcwd(), 'build', self._config['name'] + '_' + testname)

        try:
            plistlib.writePlist(plist, os.path.join(path, 'Info.plist'))
        except:
            raise FileNotWritableError('Could not write plist to target location: ', path)

        icon_name = 'Icon.svg'
        icon_path = os.path.join(os.getcwd(), 'assets', icon_name)
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.getcwd(), icon_name)
            if not os.path.exists(icon_path):
                icon_name = 'Icon.png'
                icon_path = os.path.join(os.getcwd(), 'assets', icon_name)
                if not os.path.exists(icon_path):
                    icon_path = os.path.join(os.getcwd(), icon_name)
                    if not os.path.exists(icon_path):
                        print('Could not find an Icon for your test dizmo. It is strongly recommended to add "Icon.svg" in the assets folder.')

        try:
            copy(icon_path, os.path.join(path, icon_name))
        except:
            raise FileNotWritableError('Could not write the icon "' + icon_name + '" to its target location')


class Deploy(grace.deploy.Deploy):
    def __init__(self, config):
        super(Deploy, self).__init__(config)

    def run(self, testname):
        super(Deploy, self).run(testname)

        if self._config['test']:
            dest = os.path.join(self._deployment_path, self._config['dizmo_settings']['bundle_identifier'].lower() + '.' + testname.lower())
            source = os.path.join(self._deployment_path, self._config['name'] + '_' + testname)
        elif self._config['build']:
            dest = os.path.join(self._deployment_path, self._config['dizmo_settings']['bundle_identifier'].lower())
            source = os.path.join(self._deployment_path, self._config['name'])
        else:
            raise MissingKeyError()

        self._move_deploy(source, dest)

    def _move_deploy(self, source, dest):
        if os.path.exists(dest):
            try:
                rmtree(dest)
            except:
                raise RemoveFolderError('Could not remove the deploy folder.')
        else:
            print('The dizmo will be deployed, but you need to drag & drop the folder "' + self._config['name'] + '" from the build directory into dizmospace once to allow association with it. Otherwise your dizmo will not show up as installed.')

        try:
            move(source, dest)
        except:
            raise FileNotWritableError('Could not move the deploy target to the dizmo path.')


class Zip(grace.zipit.Zip):
    def __init__(self, config):
        super(Zip, self).__init__(config)

        if 'zip_name' not in self._config:
            self._zip_name = self._config['name'] + '-' + self._config['version'] + '.dzm'


class Upload(grace.upload.Upload):
    def __init__(self, config):
        if 'urls' not in config:
            raise MissingKeyError('Could not find the dizmo_store key in either the global or local config file.')

        if 'dizmo_store' in config['urls']:
            self._base_url = config['urls']['dizmo_store']
            config['urls']['upload'] = self._base_url
        else:
            raise MissingKeyError('Could not find the dizmo_store key in either the global or local config file.')

        super(Upload, self).__init__(config)

        self._dizmo_id = self._config['dizmo_settings']['bundle_identifier']
        self._version = self._config['version']
        self._publish_latest_url = self._base_url + '/dizmo/' + self._dizmo_id + '/publish/latest'
        self._login_url = self._base_url + '/oauth/login'
        self._upload_url = self._base_url + '/dizmo'
        self._upload_url_existing = self._base_url + '/dizmo/' + self._dizmo_id

        if 'zip_name' not in self._config:
            self._zip_name = self._config['name'] + '-' + self._config['version'] + '.dzm'
            self._zip_path = os.path.join(self._cwd, 'build', self._zip_name)

    def _get_login_information(self):
        if self._username is None:
            self._username = input('Please provide the username for your upload server (or leave blank if none is required): ')

        if self._password is None:
            self._password = getpass.getpass('Please provide the password for your upload server (or leave blank if none is required): ')

        return {
            'username': self._username,
            'password': self._password
        }

    def _login_response(self, r):
        if r.status_code == 401 or r.status_code == 403:
            raise WrongLoginCredentials('Could not log in with the given credentials.')

        r = requests.get(self._publish_latest_url,
            cookies=self._cookies,
            verify=self._verify_ssl)

        self._dizmo_exist_check_response(r)

    def _dizmo_exist_check_response(self, r):
        if r.status_code == 404:
            self._upload()
            return

        if r.status_code == 200:
            self._upload_existing()
            return

        response = load_json(r.text)
        raise RemoteServerError('Error from store server (' + self._base_url + '): ' + response['errormessage'] + ' - Error Nr.: ' + str(response['errornumber']))

    def _upload_existing(self):
        if not os.path.exists(self._zip_path):
            raise FileNotFoundError('Could not find the zip file. Please check if "' + self._zip_path + '" exists.')

        try:
            zip_file = open(self._zip_path, 'r')
        except:
            raise GeneralError('Something went wrong while opening the zip file. Please try again.')

        r = requests.put(self._upload_url_existing,
            files={'file': zip_file},
            cookies=self._cookies,
            verify=self._verify_ssl
        )

        self._upload_response(r)

    def _upload_response(self, r):
        if r.status_code != 200 and r.status_code != 201:
            response = load_json(r.text)
            raise RemoteServerError('Error from store server (' + self._base_url + '): ' + response['errormessage'] + ' - Error Nr.: ' + str(response['errornumber']))


class Lint(grace.lint.Lint):
    def __init__(self, config):
        tmp = update(deepcopy(config['lintoptions']), {
            'predef': {
                'DizmoElements': True,
                'events': True,
                'bundle': True,
                'viewer': True,
                'dizmo': True,
                'DizmoHelper': True
            }
        })
        config['lintoptions'] = tmp

        super(Lint, self).__init__(config)


class Task(grace.task.Task):
    def __init__(self, task, config, module, test_cases):
        self._available_tasks = ['publish', 'unpublish']
        self._task = task
        self._subtask = ''
        self._verify_ssl = False

        try:
            super(Task, self).__init__(task, config, module, test_cases)
            return
        except UnknownCommandError as e:
            if self._task not in self._available_tasks:
                task = self._task.split(':')
                if task[0] != 'unpublish' and task[0] != 'publish' and len(task) != 2:
                    raise UnknownCommandError('The provided argument(s) could not be recognized by the manage.py script: ' + self._task)
                else:
                    if task[1] != 'display':
                        pattern = re.compile('^([0-9]+\.?)*[0-9]+$')
                        if not pattern.match(task[1]):
                            raise UnknownCommandError('The provided sub-argument for the task could not be recognized. Use either "display" or a version number (0.2, 1.5, etc.)')

                    self._task = task[0]
                    self._subtask = task[1]

    def execute(self):
        if self._task not in self._available_tasks:
            super(Task, self).execute()
            return

        self._check_config()

        self._publish_url = self._base_url + '/dizmo/' + self._dizmo_id + '/publish'
        self._login_url = self._base_url + '/oauth/login'

        self._login()

    def _check_config(self):
        if 'bundle_identifier' not in self._config['dizmo_settings']:
            raise MissingKeyError('Your bundle_identifier must be provided in the config file.')
        else:
            self._dizmo_id = self._config['dizmo_settings']['bundle_identifier']

        if 'version' not in self._config:
            raise MissingKeyError('You need to provide a version number for your dizmo in the configuration file.')
        else:
            self._version = self._config['version']

        if 'urls' not in self._config:
            raise MissingKeyError('Could not find the urls key in either the global or local config file.')

        if 'dizmo_store' not in self._config['urls']:
            raise MissingKeyError('Could not find the dizmo_store key in either the global or local config file.')
        else:
            self._base_url = self._config['urls']['dizmo_store']

        self._password = None
        self._username = None

        if 'credentials' in self._config:
            if 'username' in self._config['credentials']:
                self._username = self._config['credentials']['username']
            if 'password' in self._config['credentials']:
                self._password = self._config['credentials']['password']

    def _execute_subproject(self, project):
        if 'bundle_identifier' not in project:
            print('Not building sub project located at "' + project['source']['url'] + '" as the bundle_identifier is missing.')
            return

        super(Task, self)._execute_subproject(project)

    def _gather_option_string(self, project):
        string = super(Task, self)._gather_option_string(project)

        string += ' -o dizmo_settings:bundle_identifier_subproject=' + project['bundle_identifier']

        return string

    def _login(self):
        if self._username is None:
            self._username = input('Please provide the username for your upload server (or leave blank if none is required): ')

        if self._password is None:
            self._password = getpass.getpass('Please provide the password for your upload server (or leave blank if none is required): ')

        data = {
            'username': self._username,
            'password': self._password
        }

        r = requests.post(self._login_url,
            data=write_json(data),
            headers={'Content-type': 'application/json'},
            verify=self._verify_ssl
        )

        self._login_response(r)

    def _login_response(self, r):
        if r.status_code != 200:
            raise WrongLoginCredentials('Could not log in with the given credentials.')

        self._cookies = r.cookies

        if self._task == 'publish':
            if self._subtask == 'display':
                self._access_publish_information()
                return
            elif self._subtask == '':
                self._publish_dizmo(self._config['version'])
                return
            else:
                self._publish_dizmo(self._subtask)
        if self._task == 'unpublish':
            if self._subtask == '':
                self._unpublish_dizmo(self._config['version'])
                return
            else:
                self._unpublish_dizmo(self._subtask)

    def _publish_dizmo(self, version):
        print('Publishing dizmo with id "' + self._dizmo_id + '" and version "' + version + '".')
        self._execute_publish(True, version)

    def _unpublish_dizmo(self, version):
        print('Unpublishing dizmo with id "' + self._dizmo_id + '" and version "' + version + '".')
        self._execute_publish(False, version)

    def _execute_publish(self, state, version):
        r = requests.put(self._publish_url + '/' + version,
            data=write_json({'publish': state}),
            headers={'Content-Type': 'application/json'},
            cookies=self._cookies,
            verify=self._verify_ssl
        )

        self._display_response(r)

    def _access_publish_information(self):
        r = requests.get(self._publish_url,
            cookies=self._cookies,
            verify=self._verify_ssl)

        self._display_response(r)

    def _display_response(self, r):
        if r.status_code == 200:
            if self._task == 'publish':
                if self._subtask == 'display':
                    print(r.text)
                else:
                    print('Successfully published the dizmo.')
            if self._task == 'unpublish':
                print('Successfully removed publish status.')

            return

        response = load_json(r.text)
        raise RemoteServerError('Error from store server (' + self._base_url + '): ' + response['errormessage'] + ' - Error Nr.: ' + str(response['errornumber']))
