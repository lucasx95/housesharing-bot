# translation helper
import json
from itertools import chain
from pathlib import Path

from peewee import DoesNotExist

from python.code.model.entities import Chat


# get the translation map
def get_translation_map():
    with open(str(Path().resolve()) + '/python/resources/i18n.json') as i18n_file:
        return json.load(i18n_file)  # type: dict[str,dict[str,str] ])


translation_map = get_translation_map()  # translate a key


def translate(key, chat_id):
    try:
        return translation_map[key][Chat.get(Chat.chat_id == chat_id).language]
    except KeyError:
        return translation_map[key]['en-us']  # get the supported languages
    except DoesNotExist:
        return 'Please run /start to set language.'


TRANSLATION_OPTIONS = \
    list(set(chain.from_iterable(list(map(lambda x: list(x.keys()), list(translation_map.values()))))))

# get the supportedd languages regex
TRANSLATION_OPTIONS_REGEX = '^(' + '|'.join(TRANSLATION_OPTIONS) + ')$'
