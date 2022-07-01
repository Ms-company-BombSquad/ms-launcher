from __future__ import annotations

import json

import ba


languages = {}
LANGUAGES_DIR = ba.app.python_directory_user + '/ms_launcher/data/languages/'


def gettext(key: str, *args, **kwargs) -> str:
    """Get translated text by key."""

    language = ba.LanguageSubsystem().language.lower()
    if language not in languages:
        try:
            with open(LANGUAGES_DIR + language + '.json', 'r', encoding='utf-8') as stream:
                languages[language] = json.loads(stream.read())
        except FileNotFoundError:
            # Loading english language
            with open(LANGUAGES_DIR + 'english.json', 'r', encoding='utf-8') as stream:
                languages[language] = json.loads(stream.read())

    return languages[language].get(key, key).format(*args, **kwargs)
