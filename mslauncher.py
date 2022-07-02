from __future__ import annotations

import datetime
import ssl
import io
import json
import os
import urllib.request
import shutil
import zipfile
import threading
from typing import Optional, Union

import ba


APP_DIR = ba.app.python_directory_user
DATA_DIR = os.path.join(APP_DIR, '.ms_data')
BASE_URL = f'https://api.github.com/repos/Ms-company-BombSquad/ms-launcher/'
REPO_DIR = 'ms_launcher'
REPO_DIR_PATH = APP_DIR
PLUGIN_FILE_NAME = 'mslauncher.py'
PLUGIN_FILE = os.path.join(APP_DIR, PLUGIN_FILE_NAME)
BACKUP_PLUGIN_FILE = os.path.join(APP_DIR, 'mslauncher.backup')

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)


class Response:
    """Response for urllib"""

    def __init__(self, data) -> None:
        self.content = data

    def json(self) -> Optional[dict]:
        """JSON parse content and returns it."""
        try:
            return json.loads(self.content)
        except ValueError:
            return {}


def get(url) -> Response:
    """Send request to url and returns answer in Response instance.
    Its best to use requests here, but requests not in BombSquad libs.
    """

    context = {}
    if ba.app.platform == 'android':
        if ba.app.build_number < 20461:
            # Android builds below 1002 do not support SSL
            context = {'context': ssl.SSLContext()}

    with urllib.request.urlopen(url, **context) as res:
        return Response(res.read())


def get_latest_release() -> dict:
    """Using github API will return latest release dict."""

    releases = get(BASE_URL + 'releases').json()
    return max(releases, key=lambda r: datetime.datetime.strptime(r['published_at'], '%Y-%m-%dT%H:%M:%SZ'))


def check_update_available(latest_release: dict, current_version: str = None) -> bool:
    """Check releases for new update,
    return boolean (update available?).
    """

    if current_version is not None and latest_release['tag_name'] == current_version:
        return False
    return True


def install_from_release(latest_release: dict) -> Union[str, None]:
    """Check releases and update launcher if it need.
    Returns lasted release tag name.
    """

    zip_url = latest_release['zipball_url']
    with zipfile.ZipFile(io.BytesIO(get(zip_url).content)) as _zip:
        clear_dir(DATA_DIR)
        _zip.extractall(DATA_DIR)
        project_path = os.path.join(DATA_DIR, os.listdir(DATA_DIR)[0])
        dir_path = os.path.join(project_path, REPO_DIR)
        if not os.path.exists(dir_path):
            return
        dst_path = os.path.join(REPO_DIR_PATH, REPO_DIR)
        clear_dir(dst_path)
        shutil.copytree(dir_path, dst_path, dirs_exist_ok=True)
        new_plugin_path = os.path.join(project_path, PLUGIN_FILE_NAME)
        shutil.copyfile(PLUGIN_FILE, BACKUP_PLUGIN_FILE)
        shutil.copyfile(new_plugin_path, PLUGIN_FILE)

    ba.app.config['ms-launcher']['version'] = latest_release['tag_name']
    ba.app.config['ms-launcher']['last-update'] = get_current_date()
    ba.pushcall(ba.Call(ba.app.config.apply_and_commit), from_other_thread=True)

    return latest_release['tag_name']


def rollback_plugin() -> None:
    """Function for rollback plugin update to exists backup.
    I hope it will never be called :3
    """

    try:
        from ms_launcher.tools.translation import gettext as _
    except ImportError:
        _ = lambda text, **kwargs: text.format(**kwargs)

    txt = _('Some error occurred; rollback to backup')
    print(txt)
    pushcall_screenmessage(txt, color=(.93, .13, .13))

    shutil.copyfile(BACKUP_PLUGIN_FILE, PLUGIN_FILE)


def rollback_on_error(func: callable) -> callable:
    """Rollback plugin on error, this is decorator."""

    def wrapper(*args, **kwargs) -> any:
        try:
            result = func(*args, **kwargs)
        except:
            import traceback
            traceback.print_exc()
            return rollback_plugin()
        return result

    return wrapper


def clear_dir(path) -> bool:
    """Clear dir.
    Returns boolean (is cleared?)
    """

    if os.path.exists(path):
        shutil.rmtree(path)
        os.mkdir(path)
        return True
    return False


def get_current_date() -> str:
    """Return current date, in format ""."""

    return datetime.datetime.now().strftime("%d.%m.%Y")


def get_version() -> Optional[str]:
    """Get current version"""

    if 'ms-launcher' not in ba.app.config:
        return
    return ba.app.config['ms-launcher']['version']


def check_config() -> None:
    """Check config exists, will create it if does not exists."""

    if 'ms-launcher' not in ba.app.config:
        ba.app.config['ms-launcher'] = {
            'auto-update': True,
            'only-verified-servers': True,
            'version': None,
            'last-update': get_current_date()
        }
        ba.app.config.apply_and_commit()


def activate_launcher() -> None:
    """Activate launcher"""

    import ms_launcher
    from ms_launcher.activate import activate
    activate()


def pushcall_screenmessage(*args, **kwargs) -> None:
    """Using ba.pushcall will call ba.screenmessage"""

    from_other_thread = threading.current_thread().name != 'MainThread'
    ba.pushcall(ba.Call(ba.screenmessage, *args, **kwargs), from_other_thread=from_other_thread)


@rollback_on_error
def check_installation() -> None:
    """Check launcher installation exists.

    Will install/update launcher if it does not exists or or outdated.
    Must be called in other thread that main.
    """

    check_config()

    try:
        import ms_launcher
        ba.pushcall(activate_launcher, from_other_thread=True)
    except ImportError:
        install_from_release(get_latest_release())

        import ms_launcher
        from ms_launcher.tools.translation import gettext as _
        pushcall_screenmessage(
            _('Ms launcher v{version} has been installed successfully!', version=get_version()),
            color=(.13, .98, .13)
        )
        ba.pushcall(activate_launcher, from_other_thread=True)
    else:
        from ms_launcher.tools.translation import gettext as _
        latest_release = get_latest_release()
        update_available = check_update_available(latest_release, get_version())
        if update_available:
            if ba.app.config['ms-launcher']['auto-update']:
                install_from_release(latest_release)
                pushcall_screenmessage(
                    (
                        _('Ms launcher updated to version {version}; restart the game',
                          version=latest_release['tag_name']) + '\n' +
                        _('You can disable auto-updates in the settings')
                    ),
                    color=(.13, .98, .13)
                )
            else:
                # FIXME: Open ui window, instead of use screenmessage
                pushcall_screenmessage(
                    _('New Ms launcher update is available (v{version})', version=latest_release['tag_name']),
                    color=(.13, .98, .13)
                )


# ba_meta require api 6
# ba_meta export plugin
class Plugin(ba.Plugin):
    @rollback_on_error
    def on_app_launch(self) -> None:
        thread = threading.Thread(target=check_installation)
        thread.start()
