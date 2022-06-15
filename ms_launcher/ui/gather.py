import time
from typing import Optional

import _ba
import ba

from bastd.ui.partyqueue import PartyQueueWindow
from bastd.ui.gather.publictab import PublicGatherTab, PartyEntry

from ms_launcher.ui.launcher import LauncherWindow
from ms_launcher.tools.translation import gettext as _


# pylint: disable=access-member-before-definition,attribute-defined-outside-init


class OurPublicGatherTab(PublicGatherTab):  # pylint: disable=too-few-public-methods
    """Our public gather tab.

    Removes the required queue that appears when trying to connect to the party,
    if party.queue is not None. And adds special checkbox for display only verified servers.
    """

    def _build_join_tab(self, region_width: float,
                        region_height: float) -> None:
        c_width = region_width
        c_height = region_height - 20
        sub_scroll_height = c_height - 125
        sub_scroll_width = 830
        vertical = c_height - 35
        vertical -= 60
        filter_txt = ba.Lstr(resource='filterText')
        self._filter_text = ba.textwidget(parent=self._container,
                                          text=self._filter_value,
                                          size=(350, 45),
                                          position=(290 - 100, vertical - 10),
                                          h_align='left',
                                          v_align='center',
                                          editable=True,
                                          description=filter_txt)
        ba.widget(edit=self._filter_text, up_widget=self._join_text)
        ba.textwidget(text=filter_txt,
                      parent=self._container,
                      size=(0, 0),
                      position=(270 - 100, vertical + 13),
                      maxwidth=150,
                      scale=0.8,
                      color=(0.5, 0.46, 0.5),
                      flatness=1.0,
                      h_align='right',
                      v_align='center')
        ba.checkboxwidget(parent=self._container,
                          size=(50, 50),
                          position=(570, vertical - 10),
                          text=_('Verified servers'),
                          value=ba.app.config['ms-launcher'].get('only-verified-servers', True),
                          on_value_change_call=self.change_verified_servers_setting,
                          text_scale=0.8,
                          textcolor=(.93, .93, .93, .6),
                          color=(0.5, 0.5, 0.7))
        ba.buttonwidget(parent=self._container,
                        position=(830, vertical + 40),
                        size=(50, 50),
                        color=(0.5, 0.5, 0.7),
                        textcolor=(.93, .93, .93, .8),
                        scale=0.8,
                        autoselect=True,
                        iconscale=1.2,
                        label='MsL',
                        on_activate_call=self._on_ms_launcher_press)

        ba.textwidget(text=ba.Lstr(resource='nameText'),
                      parent=self._container,
                      size=(0, 0),
                      position=(90, vertical - 8),
                      maxwidth=60,
                      scale=0.6,
                      color=(0.5, 0.46, 0.5),
                      flatness=1.0,
                      h_align='center',
                      v_align='center')
        ba.textwidget(text=ba.Lstr(resource='gatherWindow.partySizeText'),
                      parent=self._container,
                      size=(0, 0),
                      position=(755, vertical - 8),
                      maxwidth=60,
                      scale=0.6,
                      color=(0.5, 0.46, 0.5),
                      flatness=1.0,
                      h_align='center',
                      v_align='center')
        ba.textwidget(text=ba.Lstr(resource='gatherWindow.pingText'),
                      parent=self._container,
                      size=(0, 0),
                      position=(825, vertical - 8),
                      maxwidth=60,
                      scale=0.6,
                      color=(0.5, 0.46, 0.5),
                      flatness=1.0,
                      h_align='center',
                      v_align='center')
        vertical -= sub_scroll_height + 23
        self._host_scrollwidget = scrollw = ba.scrollwidget(
            parent=self._container,
            simple_culling_v=10,
            position=((c_width - sub_scroll_width) * 0.5, vertical),
            size=(sub_scroll_width, sub_scroll_height),
            claims_up_down=False,
            claims_left_right=True,
            autoselect=True)
        self._join_list_column = ba.containerwidget(parent=scrollw,
                                                    background=False,
                                                    size=(400, 400),
                                                    claims_left_right=True)
        self._join_status_text = ba.textwidget(parent=self._container,
                                               text='',
                                               size=(0, 0),
                                               scale=0.9,
                                               flatness=1.0,
                                               shadow=0.0,
                                               h_align='center',
                                               v_align='top',
                                               maxwidth=c_width,
                                               color=(0.6, 0.6, 0.6),
                                               position=(c_width * 0.5,
                                                         c_height * 0.5))

    def change_verified_servers_setting(self, value: bool) -> None:
        """Called when a "Verified servers" button is pressed."""

        ba.app.config['ms-launcher']['only-verified-servers'] = value
        ba.app.config.apply_and_commit()

        self._query_party_list_periodically(immediately=True)

    def on_public_party_activate(self, party: PartyEntry) -> None:
        """Called when a party is clicked or otherwise activated."""

        address = party.address
        port = party.port

        now = time.time()
        last_connect_time = self._last_connect_attempt_time  # pylint: disable=access-member-before-definition
        if last_connect_time is None or now - last_connect_time > 2.0:
            _ba.connect_to_party(address, port=port)
            self._last_connect_attempt_time = now  # pylint: disable=attribute-defined-outside-init

        if party.queue is not None:
            # We will open the queue window, but if the server
            # is really not full, we will immediately enter to the server.
            ba.playsound(ba.getsound('swish'))
            PartyQueueWindow(party.queue, party.address, party.port)

    def _on_public_party_query_result(self, result: Optional[dict[str, any]]) -> None:
        """On public party query result.
        Display only verified servers if relative setting is active.
        """

        if not result:
            return super()._on_public_party_query_result(result)

        if not ba.app.config['ms-launcher'].get('only-verified-servers', True):
            return super()._on_public_party_query_result(result)

        # Ms servers ips
        verified_servers = {
            '89.108.88.73': {},
            '89.108.81.209': {},
            '194.67.121.232': {},
        }

        parties_in = result['l']
        filtered_parties_in = []
        for party_in in parties_in:
            party_ip = party_in['a']
            if party_ip in verified_servers:
                if not verified_servers[party_ip]:
                    # Allow any server on this ip
                    filtered_parties_in.append(party_in)
                    continue

                port = verified_servers[party_ip].get('port')
                name = verified_servers[party_ip].get('name')

                if party_in['p'] == port or not port:
                    if party_in['n'] == name or not name:
                        filtered_parties_in.append(party_in)

        return super()._on_public_party_query_result({'l': filtered_parties_in})

    def _query_party_list_periodically(self, immediately: bool = False) -> None:
        """Query party list periodically."""

        now = ba.time(ba.TimeType.REAL)

        # Fire off a new public-party query periodically.
        if (self._last_server_list_query_time is None
                or now - self._last_server_list_query_time > 0.001 *
                _ba.get_account_misc_read_val('pubPartyRefreshMS', 10000)
                or immediately):
            self._last_server_list_query_time = now
            if _ba.get_account_state() == 'signed_in':
                _ba.add_transaction(
                    {
                        'type': 'PUBLIC_PARTY_QUERY',
                        'proto': ba.app.protocol_version,
                        'lang': ba.app.lang.language
                    },
                    callback=ba.WeakCall(self._on_public_party_query_result))
                _ba.run_transactions()
            else:
                self._on_public_party_query_result(None)

    def _on_ms_launcher_press(self) -> None:
        """Called when ms launcher button is pressed."""

        LauncherWindow(transition='in_right')
