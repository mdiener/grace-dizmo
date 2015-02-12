import os
import plistlib
from shutil import move, rmtree, copy
import sys
from pkg_resources import resource_filename
from grace.error import MissingKeyError, WrongFormatError, FileNotWritableError, RemoveFolderError, UnknownCommandError, WrongLoginCredentials, FileUploadError
import grace.create
import grace.build
import grace.testit
import grace.zipit
import grace.deploy
import requests
import getpass
import json


def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")


def get_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, encoding))
    return os.path.dirname(unicode(__file__, encoding))


def get_plist(config, testname=None, test=False):
    if test:
        display_name = config['dizmo_settings']['display_name'] + ' ' + testname
        identifier = config['dizmo_settings']['bundle_identifier'] + '.' + testname.lower()
    else:
        display_name = config['dizmo_settings']['display_name']
        identifier = config['dizmo_settings']['bundle_identifier']

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
        Category=config['dizmo_settings']['category']
    )

    if config['dizmo_settings']['elements_version'] != 'none':
        plist['ElementsVersion'] = config['dizmo_settings']['elements_version']

    if config['dizmo_settings']['hidden_dizmo']:
        plist['hiddenDizmo'] = config['dizmo_settings']['hidden_dizmo']

    return plist


class Config:
    def __init__(self, config):
        self._config = config

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

        try:
            self._check_config()
        except:
            raise

    def _check_config(self):
        if 'dizmo_settings' not in self._config:
            raise MissingKeyError('Could not find settings for dizmo.')

        self._dizmo_config = self._config['dizmo_settings']

        if 'display_name' not in self._dizmo_config:
            raise MissingKeyError('Specify a display name in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['display_name'], unicode):
                raise WrongFormatError('The display_name key needs to be a string.')
            else:
                if len(self._dizmo_config['display_name']) == 0:
                    raise WrongFormatError('The display_name has to consist of at least one character.')

        if 'bundle_name' not in self._dizmo_config:
            raise MissingKeyError('Please specify a "bundle_name" under the dizmo_settings key in your project.cfg file.')
        else:
            if not isinstance(self._dizmo_config['bundle_name'], unicode):
                raise WrongFormatError('The bundle_name key needs to be a string.')
            else:
                if len(self._dizmo_config['bundle_name']) == 0:
                    raise WrongFormatError('The bundle_name needs to be at least one character long.')

        if 'bundle_identifier' not in self._dizmo_config:
            raise MissingKeyError('Specify a bundle identifier in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['bundle_identifier'], unicode):
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
            if not isinstance(self._dizmo_config['description'], unicode):
                raise WrongFormatError('The description needs to be a unicode string.')
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
            if not isinstance(self._dizmo_config['category'], unicode):
                raise WrongFormatError('The category needs to be a unicode string.')
            else:
                if len(self._dizmo_config['category']) == 0:
                    raise WrongFormatError('The category has to consist of at least one character.')
                if self._dizmo_config['category'] not in self._categories:
                    raise WrongFormatError('The category has to be one of the following: "books_and_references", "comics", "communication", "education", "entertainment", "finance", "games", "health_and_fitness", "libraries_and_demo", "lifestyle", "media_and_video", "medical", "music_and_audio", "news_and_magazines", "personalization", "photography", "productivity", "shopping", "social", "sports", "tools", "transportation", "travel_and_local", "weather"')

        if 'min_space_version' not in self._dizmo_config:
            raise MissingKeyError('Add a min_space_version in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['min_space_version'], unicode):
                raise WrongFormatError('The min_space_version needs to be unicode string.')
            else:
                if len(self._dizmo_config['min_space_version']) == 0:
                    raise WrongFormatError('The min_space_version has to consist of at least one character.')

        if 'change_log' not in self._dizmo_config:
            raise MissingKeyError('Add a change_log in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['change_log'], unicode):
                raise WrongFormatError('The change_log needs to be unicode string.')
            else:
                if len(self._dizmo_config['change_log']) == 0:
                    raise WrongFormatError('The change_log has to consist of at least one character.')

        if 'api_version' not in self._dizmo_config:
            raise MissingKeyError('Specify an api version in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['api_version'], unicode):
                raise WrongFormatError('The api_version key needs to be a string.')
            else:
                if len(self._dizmo_config['api_version']) == 0:
                    raise WrongFormatError('The api_version has to consist of at least one character.')

        if 'main_html' not in self._dizmo_config:
            raise MissingKeyError('Specify a main html in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['main_html'], unicode):
                raise WrongFormatError('The main_html key needs to be a string.')
            else:
                if len(self._dizmo_config['main_html']) == 0:
                    raise WrongFormatError('The main_html has to consist of at least one character.')

        if 'hidden_dizmo' not in self._dizmo_config:
            self._config['dizmo_settings']['hidden_dizmo'] = False

        if 'elements_version' not in self._dizmo_config:
            self._config['dizmo_settings']['elements_version'] = 'none'

    def get_config(self):
        return self._config


class New(grace.create.New):
    def __init__(self, projectName):
        self._projectName = projectName
        self._root = get_path()
        self._cwd = os.getcwd()

        try:
            self._skeleton_path = resource_filename(__name__, os.path.join('skeleton', 'dizmo'))
        except NotImplementedError:
            self._skeleton_path = os.path.join(sys.prefix, 'skeleton', 'dizmo')

        self._projectPath = os.path.join(self._cwd, self._projectName)

        self._copy_structure()
        self._replace_strings()


class Build(grace.build.Build):
    def __init__(self, config):
        super(Build, self).__init__(config)

    def run(self):
        super(Build, self).run()

        plist = get_plist(self._config)
        path = self._config['build_path']

        assets_path = os.path.join(path, 'assets')

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

        try:
            plistlib.writePlist(plist, os.path.join(path, 'Info.plist'))
        except:
            raise FileNotWritableError('Could not write plist to target location: ', path)

        if os.path.isfile(image_PNG_source):
            try:
                copy(image_PNG_source, os.path.join(path, 'Icon.png'))
            except:
                print 'Could not copy your Icon.png file.'

        if os.path.isfile(image_PNG_dark_source):
            try:
                copy(image_PNG_dark_source, os.path.join(path, 'Icon-dark.png'))
            except:
                print 'Could not copy your Icon-dark.png file.'

        if os.path.isfile(image_SVG_source):
            try:
                copy(image_SVG_source, os.path.join(path, 'Icon.svg'))
            except:
                print 'Could not copy your Icon.svg file.'

        if os.path.isfile(image_SVG_dark_source):
            try:
                copy(image_SVG_dark_source, os.path.join(path, 'Icon-dark.svg'))
            except:
                print 'Could not copy your Icon-dark.svg file.'

        if os.path.isfile(image_preview_source):
            try:
                copy(image_preview_source, os.path.join(path, 'Preview.png'))
            except:
                print 'Could not copy your Preview.png file.'

        if os.path.exists(assets_path):
            try:
                rmtree(assets_path)
            except:
                print ('Could not delete your assets folder in the build folder.')


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

        try:
            copy(os.path.join(os.getcwd(), 'Icon.png'), os.path.join(path, 'Icon.png'))
        except:
            print 'Could not find an icon for your dizmo. You should consider placing a `Icon.png` in your root folder.'


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

        try:
            move(source, dest)
        except:
            raise FileNotWritableError('Could not move the deploy target to the dizmo path.')


class Zip(grace.zipit.Zip):
    def __init__(self, config):
        super(Zip, self).__init__(config)

    def run(self, testname):
        super(Zip, self).run(testname)

        if self._config['test']:
            name = self._config['name'] + '_' + testname
        elif self._config['build']:
            name = self._config['name']
        else:
            raise MissingKeyError()

        source = os.path.join(os.getcwd(), 'build', name + '_v' + self._config['version'] + '.zip')
        dest = os.path.join(os.getcwd(), 'build', name + '_v' + self._config['version'] + '.dzm')

        try:
            self._move_zip(source, dest)
        except:
            raise

        if self._zip_path is not None:
            source = os.path.join(self._zip_path, name + '_v' + self._config['version'] + '.zip')
            dest = os.path.join(self._zip_path, name + '_v' + self._config['version'] + '.dzm')

            try:
                self._move_zip(source, dest)
            except:
                raise

    def _move_zip(self, source, dest):
        if os.path.exists(dest):
            try:
                os.remove(dest)
            except:
                raise FileNotWritableError('Could not remove the old dizmo zip file.')

        try:
            move(source, dest)
        except:
            raise FileNotWritableError('Could not move the zip target to the dizmo path.')


class Upload(grace.upload.Upload):
    def __init__(self, config):
        self._cwd = os.getcwd()
        self._root = get_path()
        self._config = config
        self._verify_ssl = False

        self._check_config()

        self._publish_latest_url = self._base_url + '/dizmo/' + self._dizmo_id + '/publish/latest'
        self._login_url = self._base_url + '/oauth/login'
        self._upload_url = self._base_url + '/dizmo'
        self._upload_url_existing = self._base_url + '/dizmo/' + self._version

        self._zip_name = self._config['name'] + '_v' + self._config['version'] + '.dzm'
        self._zip_path = os.path.join(self._cwd, 'build', self._zip_name)

    def _check_config(self):
        if 'urls' not in self._config['dizmo_settings']:
            if 'urls' not in self._config:
                raise MissingKeyError('Could not find the urls key in either the global or local config file.')

        if 'dizmo_store' not in self._config['dizmo_settings']['urls']:
            if 'dizmo_store' not in self._config['urls']:
                raise MissingKeyError('Could not find the dizmo_store key in either the global or local config file.')
            else:
                self._base_url = self._config['urls']['dizmo_store']
        else:
            self._base_url = self._config['dizmo_settings']['urls']['dizmo_store']

        if 'bundle_identifier' not in self._config['dizmo_settings']:
            raise MissingKeyError('Could not find the bundle_identifier in your configuration file.')
        else:
            self._dizmo_id = self._config['dizmo_settings']['bundle_identifier']

        if 'version' not in self._config:
            raise MissingKeyError('Could not find version in your configuration file.')
        else:
            self._version = self._config['version']

        if 'credentials' not in self._config['dizmo_settings']:
            if 'credentials' not in self._config:
                self._username = ''
                self._password = ''
        else:
            if 'username' in self._config['dizmo_settings']['credentials']:
                self._username = self._config['dizmo_settings']['credentials']['username'].encode()
            else:
                if 'username' in self._config['credentials']:
                    self._username = self._config['credentials']['username'].encode()
                else:
                    self._username = ''

            if 'password' in self._config['dizmo_settings']['credentials']:
                self._password = self._config['dizmo_settings']['credentials']['password'].encode()
            else:
                if 'password' in self._config['credentials']:
                    self._password = self._config['credentials']['password'].encode()
                else:
                    self._password = ''

    def _login_response(self, r):
        if r.status_code != 200:
            raise WrongLoginCredentials('Could not log in with the given credentials.')

        r = requests.get(self._publish_latest_url,
            cookies=self._cookies,
            verify=self._verify_ssl
        )

        self._dizmo_exist_check_response(r)

    def _dizmo_exist_check_response(self, r):
        if r.status_code == 404:
            self._upload()

        if r.status_code == 200:
            self._upload_existing()

        response = json.loads(r.text)
        raise FileUploadError(response['errormessage'] + ' - Error Nr.: ' + str(response['errornumber']))

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
        if r.status_code != 200 or r.status_code != 201:
            response = json.loads(r.text)
            raise FileUploadError(response['errormessage'] + ' - Error Nr.: ' + str(response['errornumber']))


class Task(grace.task.Task):
    def __init__(self, tasks, config, module):
        self._available_tasks = ['publish', 'unpublish', 'publish:display']
        self._task = tasks[0]
        self._verify_ssl = False

        try:
            super(Task, self).__init__(tasks, config, module)
            return
        except UnknownCommandError as e:
            if self._task not in self._available_tasks:
                raise UnknownCommandError('The provided argument(s) could not be recognized by the manage.py script: ' + self._task)

    def execute(self):
        if self._task not in self._available_tasks:
            super(Task, self).execute()
            return

        self._check_config()

        self._publish_url = self._base_url + '/dizmo/' + self._dizmo_id + '/publish/' + self._version
        self._publish_info_url = self._base_url + '/dizmo/' + self._dizmo_id + '/publish'
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

        if 'urls' not in self._config['dizmo_settings']:
            if 'urls' not in self._config:
                raise MissingKeyError('Could not find the urls key in either the global or local config file.')

        if 'dizmo_store' not in self._config['dizmo_settings']['urls']:
            if 'dizmo_store' not in self._config['urls']:
                raise MissingKeyError('Could not find the dizmo_store key in either the global or local config file.')
            else:
                self._base_url = self._config['urls']['dizmo_store']
        else:
            self._base_url = self._config['dizmo_settings']['urls']['dizmo_store']

        if 'credentials' not in self._config['dizmo_settings']:
            if 'credentials' not in self._config:
                self._username = ''
                self._password = ''
        else:
            if 'username' in self._config['dizmo_settings']['credentials']:
                self._username = self._config['dizmo_settings']['credentials']['username'].encode()
            else:
                if 'username' in self._config['credentials']:
                    self._username = self._config['credentials']['username'].encode()
                else:
                    self._username = ''

            if 'password' in self._config['dizmo_settings']['credentials']:
                self._password = self._config['dizmo_settings']['credentials']['password'].encode()
            else:
                if 'password' in self._config['credentials']:
                    self._password = self._config['credentials']['password'].encode()
                else:
                    self._password = ''

    def _login(self):
        if self._username == '':
            self._username = raw_input('Please provide the username for your upload server (or leave blank if none is required): ')

        if self._password == '':
            self._password = getpass.getpass('Please provide the password for your upload server (or leave blank if none is required): ')

        data = {}

        if self._username != '':
            data['username'] = self._username
        if self._password != '':
            data['password'] = self._password

        r = requests.post(self._login_url,
            data=json.dumps(data),
            headers={'Content-type': 'application/json'},
            verify=self._verify_ssl
        )

        self._login_response(r)

    def _login_response(self, r):
        if r.status_code != 200:
            raise WrongLoginCredentials('Could not log in with the given credentials.')

        self._cookies = r.cookies

        if self._task == 'publish:display':
            self._access_publish_information()
        if self._task == 'publish':
            self._publish_dizmo()
        if self._task == 'unpublish':
            self._unpublish_dizmo()

    def _publish_dizmo(self):
        print('Publishing dizmo with id: ' + self._dizmo_id + ' and version: ' + self._config['version'])
        self._execute_publish(True)

    def _unpublish_dizmo(self):
        print('Unpublishing dizmo with id: ' + self._dizmo_id + ' and version: ' + self._config['version'])
        self._execute_publish(False)

    def _execute_publish(self, state):
        r = requests.put(self._publish_url,
            data=json.dumps({'publish': state}),
            headers={'Content-Type': 'application/json'},
            cookies=self._cookies,
            verify=self._verify_ssl
        )

        self._display_response(r)

    def _access_publish_information(self):
        r = requests.get(self._publish_info_url,
            cookies=self._cookies,
            verify=self._verify_ssl
        )

        self._display_response(r)

    def _display_response(self, r):
        if r.status_code == 200:
            if self._task == 'publish':
                print('Successfully published the dizmo.')
            if self._task == 'unpublish':
                print('Successfully removed publish status.')
            if self._task == 'publish:display':
                print(r.text)

        response = json.loads(r.text)
        raise FileUploadError(response['errormessage'] + ' - Error Nr.: ' + str(response['errornumber']))
