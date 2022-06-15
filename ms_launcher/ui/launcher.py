import ba

from ms_launcher import __version__
from ms_launcher.tools.translation import gettext as _


class LauncherWindow(ba.Window):  # pylint: disable=too-few-public-methods
    """Window for display info about launcher & settings."""

    def __init__(self, transition: str = 'in_right') -> None:
        uiscale = ba.app.ui.uiscale
        self._width = width = 580
        self._height = height = (350 if uiscale is ba.UIScale.SMALL else
                                 420 if uiscale is ba.UIScale.MEDIUM else 520)

        self._scroll_width = self._width - 100
        self._scroll_height = self._height - 120

        _sub_width = self._scroll_width * 0.95
        _sub_height = self._height * 0.7
        uiscale = ba.app.ui.uiscale
        super().__init__(root_widget=ba.containerwidget(
            size=(width, height),
            transition=transition,
            scale=(2.35 if uiscale is ba.UIScale.SMALL else
                   1.55 if uiscale is ba.UIScale.MEDIUM else 1.0),
            stack_offset=(0, -30) if uiscale is ba.UIScale.SMALL else (0, 0)))

        back_btn = ba.buttonwidget(
            parent=self._root_widget,
            position=(40, height - 67),
            size=(120, 60),
            scale=0.8,
            autoselect=True,
            label=ba.Lstr(resource='doneText'),
            on_activate_call=self._cancel)
        ba.containerwidget(edit=self._root_widget, cancel_button=back_btn)

        ba.textwidget(parent=self._root_widget,
                      position=(self._width * 0.5, self._height - 45),
                      size=(20, 20),
                      h_align='center',
                      v_align='center',
                      text="Ms Launcher",
                      scale=0.7,
                      color=(1, 1, 1))

        self._scrollwidget = ba.scrollwidget(parent=self._root_widget,
                                             position=(50, 50),
                                             simple_culling_v=20.0,
                                             highlight=False,
                                             size=(_sub_width, _sub_height),
                                             selection_loops_to_parent=True)

        self._subcontainer = ba.columnwidget(parent=self._scrollwidget,
                                             border=15,
                                             selection_loops_to_parent=True)
        ba.textwidget(parent=self._subcontainer,
                      position=(20, 0),
                      size=(200, 20),
                      h_align='left',
                      text=_("Version: {version}", version=__version__),
                      color=(1, 1, 1))
        last_update = ba.app.config['ms-launcher'].get('last-update', '-')
        ba.textwidget(parent=self._subcontainer,
                      position=(20, 0),
                      size=(200, 20),
                      h_align='left',
                      text=_("Last updated on: {date}", date=last_update),
                      color=(1, 1, 1))
        ba.checkboxwidget(parent=self._subcontainer,
                          size=(50, 50),
                          position=(20, 0),
                          text=_('Auto update'),
                          value=ba.app.config['ms-launcher'].get('auto-update', True),
                          on_value_change_call=self.change_auto_update_setting,
                          text_scale=0.8,
                          textcolor=(.93, .93, .93, .6),
                          color=(0.5, 0.5, 0.7))

    def change_auto_update_setting(self, value: bool) -> None:
        """Called when "Auto update" button is pressed."""

        ba.app.config['ms-launcher']['auto-update'] = value
        ba.app.config.apply_and_commit()

    def _cancel(self) -> None:
        ba.containerwidget(
            edit=self._root_widget,
            transition='out_right')
