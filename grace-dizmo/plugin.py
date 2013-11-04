import os
import plistlib
from shutil import move, rmtree, copy
import sys
from pkg_resources import resource_filename


def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")


def get_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, encoding))
    return os.path.dirname(unicode(__file__, encoding))


class Dizmo:
    def __init__(self):
        self._dizmo_deployment_path = os.path.join(os.path.expanduser('~'), '.local', 'share', 'data', 'futureLAB', 'dizmode', 'InstalledWidgets')
        if sys.platform.startswith('win32'):
            userdir = os.path.expanduser('~user')[:-4]
            self._dizmo_deployment_path = os.path.join(userdir, 'dizmo', 'dizmo', 'InstalledDizmos')
            self._dizmo_deployment_path = self._dizmo_deployment_path.replace('\\', '\\\\')
        if sys.platform.startswith('darwin'):
            self._dizmo_deployment_path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'dizmo', 'InstalledDizmos')

    def skeleton_path(self):
        try:
            skeleton = resource_filename(__name__, os.path.join('skeleton', 'dizmo'))
        except NotImplementedError:
            skeleton = os.path.join(sys.prefix, 'skeleton', 'dizmo')

        return skeleton

    def pass_config(self, config):
        self._config = config
        try:
            self._check_config()
        except:
            raise

        self._bundle_name = self._dizmo_config['bundle_identifier'].split('.')
        self._bundle_name = self._bundle_name[len(self._bundle_name) - 1]

    def _check_config(self):
        if 'dizmo_settings' not in self._config:
            raise MissingKeyError('Could not find settings for dizmo.')

        self._dizmo_config = self._config['dizmo_settings']

        if 'development_region' not in self._dizmo_config:
            raise MissingKeyError('Specify a development region in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['development_region'], unicode):
                raise WrongFormatError('The development_region key needs to be a string.')
            else:
                if len(self._dizmo_config['development_region']) == 0:
                    raise WrongFormatError('The development_region has to consist of at least one character.')

        if 'display_name' not in self._dizmo_config:
            raise MissingKeyError('Specify a display name in your config file under `dizmo_settings`.')
        else:
            if not isinstance(self._dizmo_config['display_name'], unicode):
                raise WrongFormatError('The display_name key needs to be a string.')
            else:
                if len(self._dizmo_config['display_name']) == 0:
                    raise WrongFormatError('The display_name has to consist of at least one character.')

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

        if 'hidden_widget' not in self._dizmo_config:
            self._dizmo_config['hidden_widget'] = False

    def _get_plist(self, test=False):
        if test:
            display_name = self._dizmo_config['display_name'] + ' Test'
            identifier = self._dizmo_config['bundle_identifier'] + '.test'
        else:
            display_name = self._dizmo_config['display_name']
            identifier = self._dizmo_config['bundle_identifier']

        return dict(
            CFBundleDevelopmentRegion=self._dizmo_config['development_region'],
            CFBundleDisplayName=display_name,
            CFBundleIdentifier=identifier,
            CFBundleName=self._bundle_name,
            CFBundleShortVersionString=self._config['version'],
            CFBundleVersion=self._config['version'],
            CloseBoxInsetX=self._dizmo_config['box_inset_x'],
            CloseBoxInsetY=self._dizmo_config['box_inset_y'],
            MainHTML=self._dizmo_config['main_html'],
            Width=self._dizmo_config['width'],
            Height=self._dizmo_config['height'],
            KastellanAPIVersion=self._dizmo_config['api_version'],
            hiddenWidget=self._dizmo_config['hidden_widget']
        )

    def after_build(self):
        plist = self._get_plist()
        path = self._config['build_path']
        imagePNGSource = os.path.join(os.getcwd(), 'Icon.png')
        imageSVGSource = os.path.join(os.getcwd(), 'Icon.svg')

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

    def after_test(self):
        plist = self._get_plist(test=True)
        path = self._config['test_build_path']

        try:
            plistlib.writePlist(plist, os.path.join(path, 'Info.plist'))
        except:
            raise FileNotWritableError('Could not write plist to target location: ', path)

        try:
            copy(os.path.join(os.getcwd(), 'Icon.png'), os.path.join(path, 'Icon.png'))
        except:
            print 'Could not find an icon for your dizmo. You should consider placing a `Icon.png` in your root folder.'

    def new_replace_line(self, line):
        line = line.replace('#DIZMODEPLOYMENTPATH', self._dizmo_deployment_path)

        return line

    def after_deploy(self):
        if self._config['test']:
            source = os.path.join(self._config['deployment_path'], self._config['name'] + '_test')
            dest = os.path.join(self._config['deployment_path'], self._dizmo_config['bundle_identifier'] + '.test')

            try:
                self._move_deploy(source, dest)
            except:
                raise

        if self._config['build']:
            source = os.path.join(self._config['deployment_path'], self._config['name'])
            dest = os.path.join(self._config['deployment_path'], self._dizmo_config['bundle_identifier'])

            try:
                self._move_deploy(source, dest)
            except:
                raise

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

    def after_zip(self):
        if self._config['test']:
            try:
                self._move_zip(self._config['name'] + '_test')
            except:
                raise

        if self._config['build']:
            try:
                self._move_zip(self._config['name'])
            except:
                raise

    def _move_zip(self, name):
        try:
            source = os.path.join(self._config['zip_path'], name + '_v' + self._config['version'] + '.zip')
            dest = os.path.join(self._config['zip_path'], name + '_v' + self._config['version'] + '.dzm')
        except:
            source = os.path.join(os.getcwd(), 'build', name + '_v' + self._config['version'] + '.zip')
            dest = os.path.join(os.getcwd(), 'build', name + '_v' + self._config['version'] + '.dzm')

        if os.path.exists(dest):
            try:
                os.remove(dest)
            except:
                raise FileNotWritableError('Could not remove the old dizmo zip file.')

        try:
            move(source, dest)
        except:
            raise FileNotWritableError('Could not move the zip target to the dizmo path.')


class Error(Exception):
    def __init__(self, msg='', arg=None):
        if arg:
            self.msg = msg + arg
        else:
            self.msg = msg

    def __repr__(self):
        return self.msg


class FileNotWritableError(Error):
    pass


class RemoveFolderError(Error):
    pass


class MissingKeyError(Error):
    pass

class WrongFormatError(Error):
    pass
