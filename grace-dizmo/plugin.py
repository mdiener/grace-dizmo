import os
import plistlib
from shutil import move, rmtree, copy
import sys
from pkg_resources import resource_filename
from grace.error import MissingKeyError, WrongFormatError, FileNotWritableError, RemoveFolderError, UnknownCommandError
import grace.create
import grace.build
import grace.testit
import grace.zipit
import grace.deploy


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
        imagePNGSource = os.path.join(os.getcwd(), 'Icon.png')
        imageSVGSource = os.path.join(os.getcwd(), 'Icon.svg')
        imagePreviewSource = os.path.join(os.getcwd(), 'Preview.png')

        try:
            plistlib.writePlist(plist, os.path.join(path, 'Info.plist'))
        except:
            raise FileNotWritableError('Could not write plist to target location: ', path)

        if os.path.isfile(imagePNGSource):
            try:
                copy(imagePNGSource, os.path.join(path, 'Icon.png'))
            except:
                print 'Could not copy your Icon.png file.'

        if os.path.isfile(imageSVGSource):
            try:
                copy(imageSVGSource, os.path.join(path, 'Icon.svg'))
            except:
                print 'Could not copy your Icon.svg file.'

        if os.path.isfile(imagePreviewSource):
            try:
                copy(imagePreviewSource, os.path.join(path, 'Preview.png'))
            except:
                print 'Could not copy your Preview.png file.'


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


class Task(grace.task.Task):
    def __init__(self, tasks, config, module):
        self._tasks = ['publish', 'unpublish']
        self._task = None

        try:
            super(Task, self).__init__(tasks, config, module)
            return
        except UnknownCommandError as e:
            if task not in self._tasks:
                raise UnknownCommandError('The provided argument(s) could not be recognized by the manage.py script: ' + task)

        self._task = task
        self._check_config()

    def _check_config(self):
        if 'dizmoid' not in self._config:
            if 'dizmoid' not in self._global_config:
                raise MissingKeyError('Your dizmoid must be provided in the config file (either globally or locally).')
        if 'email' not in self._config:
            if 'email' not in self._global_config:
                raise MissingKeyError('Your email must be provided in the config file (either globally or locally).')

    def execute(self):
        if self._task == 'publish':
            self._execute_publish()
            return
        if self._task == 'unpublish':
            self._execute_unpublish()
            return

        super(Task, self).execute()

    def _execute_unpublish(self):
        # ToDo unpublish function
        pass

    def _execute_publish(self):
        # ToDo publish function
        pass
