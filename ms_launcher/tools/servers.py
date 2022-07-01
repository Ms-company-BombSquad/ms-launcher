from __future__ import annotations

import json

import ba


VERIFIED_SERVERS_FILE = ba.app.python_directory_user + '/ms_launcher/data/verified_servers.json'


def get_verified_servers() -> dict:
    """Getting servers from file and return its in dict format,
    where keys is IPs and values is fields for filtering (port, server name).
    """

    with open(VERIFIED_SERVERS_FILE, 'r', encoding='utf-8') as stream:
        return json.loads(stream.read())
