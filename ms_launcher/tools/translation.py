import ba
import json


class Trans:
    """Base class for get translations.
    Cache loaded language files to Trans.languages
    """

    languages = {}
    languages_dir = 'ms_launcher/data/languages/'

    def __getattr__(self, key: str):
        language = ba.LanguageSubsystem().language.lower()
        if language in self.languages:
            try:
                with open(self.languages_dir + language + '.json', 'r', encoding='utf-8') as f:
                    self.languages[language] = json.loads(f.read())
            except FileNotFoundError:
                # Loading english language
                with open(self.languages_dir + 'english.json', 'r', encoding='utf-8') as f:
                    self.languages[language] = json.loads(f.read())

        return self.languages[language].get(key)


_trans = Trans()


def gettext(key: str, *args, **kwargs) -> str:
    """Get translated text by key."""

    return _trans.get(key, key).format(*args, **kwargs)
