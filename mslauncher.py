import os
import platform
import subprocess
import sys
from threading import Thread

import ba


def get_python_version() -> str:
    """Return python version for BombSquad build."""

    build_num = ba.app.build_number
    if build_num >= 20591:
        return '3.10'
    elif build_num >= 20394:
        return '3.9'
    elif build_num >= 20163:
        return '3.8'
    else:
        return '3.7'


def get_python_bin() -> str:
    """Return python bin."""

    python_version = get_python_version()
    return f'python{python_version}' if platform.system() != 'Windows' else 'python'


def check_config() -> None:
    """Check config exists, will create it if does not exists."""

    if 'ms-launcher' not in ba.app.config:
        ba.app.config['ms-launcher'] = {
            'auto-update': True,
            'only-verified-servers': True,
        }
        ba.app.config.apply_and_commit()


def activate_launcher() -> None:
    """Activate launcher"""

    import ms_launcher
    from ms_launcher.activate import activate
    activate()
    print(f'MS Launcher v{ms_launcher.__version__} has been successfully activated; enjoy')


def check_installation() -> None:
    """Check launcher installation exists.

    Will install/update launcher if it does not exists or or outdated.
    Must be called in other thread that main.
    """

    check_config()
    bs_libs = ba.app.python_directory_user
    python_bin = get_python_bin()

    try:
        import ms_launcher
        ba.pushcall(activate_launcher, from_other_thread=True)
    except ImportError:
        result = subprocess.run(
            [python_bin, '-m', 'pip', 'install', 'ms-launcher', '--no-cache-dir', f'--target={bs_libs}'],
            check=True,
            capture_output=True).stdout.decode().strip().lower()

        import ms_launcher
        from ms_launcher.tools.translation import gettext as _
        ba.pushcall(ba.Call(
            ba.screenmessage,
            _('Ms launcher v{version} has been installed successfully!', version=ms_launcher.__version__),
            color=(.13, .98, 1.3)
            ), from_other_thread=True
        )
        ba.pushcall(activate_launcher, from_other_thread=True)
    else:
        from ms_launcher.tools.translation import gettext as _
        check_version = subprocess.run(
            [python_bin, '-m', 'pip', 'index', 'versions', 'ms-launcher'],
            check=True,
            capture_output=True).stdout.decode().strip().lower().splitlines()
        last_version = [line for line in check_version if 'latest' in line][0].split(':')[-1].strip()

        if ms_launcher.__version__ != last_version:
            if ba.app.config['ms-launcher']['auto-update']:
                subprocess.run(
                    [python_bin, '-m', 'pip',
                     'install', 'ms-launcher', '--upgrade',
                     '--no-cache-dir', f'--target={bs_libs}'],
                    capture_output=True
                )
                ba.pushcall(ba.Call(
                    ba.screenmessage,
                    (
                        _('Ms launcher updated to version {version}; restart the game', version=last_version) + '\n' +
                        _('You can disable auto-updates in the settings')
                    ),
                    color=(.13, .98, 1.3)
                    ), from_other_thread=True
                )
            else:
                # FIXME: Open ui window, instead of use screenmessage
                ba.pushcall(ba.Call(
                    ba.screenmessage,
                    _('New Ms launcher update is available (v{version})', version=last_version),
                    color=(.13, .98, 1.3)
                    ), from_other_thread=True
                )


def check_installation_old() -> None:
    """Check launcher installation exists.
    Will install/update launcher if it does not exists or or outdated.
    """

    check_config()
    bs_libs = ba.app.python_directory_user
    python_bin = get_python_bin()

    result = subprocess.run(
        [python_bin, '-m', 'pip', 'install', 'ms-launcher', '--no-cache-dir', f'--target={bs_libs}'],
        check=True,
        capture_output=True).stdout.decode().strip().lower()
    print(result)
    check_version = subprocess.run(
        [python_bin, '-m', 'pip', 'index', 'versions', 'ms-launcher'],
        check=True,
        capture_output=True).stdout.decode().strip().lower().splitlines()
    print(check_version)
    current_version = [line for line in check_version if 'installed' in line][0].split(':')[-1].strip()
    last_version = [line for line in check_version if 'latest' in line][0].split(':')[-1].strip()

    def lol(*args, **kwargs):
        print('screen:', *args, kwargs)
        old_screenmessage(*args, **kwargs)

    old_screenmessage = ba.screenmessage
    ba.screenmessage = lol
    # Activate launcher
    import ms_launcher
    from ms_launcher.tools.translation import gettext as _
    if 'downloading' in result:
        ba.pushcall(ba.Call(ba.screenmessage,
                    _('Ms launcher v{version} has been installed successfully!', version=current_version),
                    color=(.13, .98, 1.3)
                    ), from_other_thread=True)
    elif 'requirement already satisfied' in result:
        if current_version != last_version:
            if ba.app.config['ms-launcher']['auto-update']:
                subprocess.run(
                    [python_bin,
                     '-m',
                     'pip',
                     'install',
                     'ms-launcher',
                     '--upgrade',
                     '--no-cache-dir',
                     f'--target={bs_libs}']
                )
                ba.screenmessage(
                    (
                        _('Ms launcher updated to version {version}', version=last_version) + '\n' +
                        _('You can disable auto-updates in the settings')
                    ),
                    color=(.13, .98, 1.3)
                )
            else:
                # FIXME: Open ui window, instead of use screenmessage
                ba.screenmessage(
                    _('New Ms launcher update is available (v{version})', version=last_version),
                    color=(.13, .98, 1.3)
                )


# ba_meta require api 6
# ba_meta export plugin
class Plugin(ba.Plugin):
    def on_app_launch(self) -> None:
        thread = Thread(target=check_installation)
        thread.start()
