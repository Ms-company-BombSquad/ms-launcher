import datetime
import platform
import subprocess
import time
import io
import json
import os
import urllib.request
import shutil
import zipfile
from threading import Thread
from typing import Optional, Union

import ba


APP_DIR = ba.app.python_directory_user
DATA_DIR = os.path.join(APP_DIR, '.ms_data')
BASE_URL = f'https://api.github.com/repos/Ms-company-BombSquad/ms-launcher/'
REPO_DIR = 'ms_launcher'
REPO_DIR_PATH = APP_DIR

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

    with urllib.request.urlopen(url) as res:
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
        print('We are in install_from_release on with zipfile')
        clear_dir(DATA_DIR)
        print('cleared data from .ms_data')
        _zip.extractall(DATA_DIR)
        print('zip extracted')
        project_path = os.path.join(DATA_DIR, os.listdir(DATA_DIR)[0])
        print(f'project path: {project_path}')
        dir_path = os.path.join(project_path, REPO_DIR)
        print(f'dir path: {dir_path}')
        if not os.path.exists(dir_path):
            print(f'Path "{dir_path}" does not exists')
            return
        dst_path = os.path.join(REPO_DIR_PATH, REPO_DIR)
        print(f'dst path: {dst_path}')
        clear_dir(dst_path)
        print(f'dst path cleared')
        shutil.copytree(dir_path, dst_path, dirs_exist_ok=True)
        print(f'shutil.copytree from {dir_path} to {dst_path}')

    print('editing config')
    ba.app.config['ms-launcher']['version'] = latest_release['tag_name']
    ba.app.config['ms-launcher']['last-update'] = get_current_date()
    ba.pushcall(ba.Call(ba.app.config.apply_and_commit), from_other_thread=True)
    print(f'config commit; return {latest_release["tag_name"]}')

    return latest_release['tag_name']


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
    print(f'MS Launcher v{get_version()} has been successfully activated; enjoy')


def pushcall_screenmessage(*args, **kwargs) -> None:
    """Using ba.pushcall will call ba.screenmessage"""

    ba.pushcall(ba.Call(ba.screenmessage, *args, **kwargs), from_other_thread=True)


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
    def on_app_launch(self) -> None:
        thread = Thread(target=check_installation)
        thread.start()
