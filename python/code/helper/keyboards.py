from telegram import ReplyKeyboardMarkup

from python.code.helper.translator import TRANSLATION_OPTIONS, translation_map
from python.code.model.entities import Chat, DoesNotExist

# get supported languages keyboard
# language keyboard
LANGUAGES_KEYBOARD = list(map(lambda lang: [lang], TRANSLATION_OPTIONS))


# get languages keboard
def get_languages_keyboard():
    return ReplyKeyboardMarkup(LANGUAGES_KEYBOARD
                               , one_time_keyboard=True)


# days keybard
DAYS_KEYBOARD = [list(map(lambda x: str(x).zfill(2), range(1, 10))), list(map(str, range(11, 20))),
                 list(map(str, range(21, 30))), ['31'] + ['--'] * 9]


# get days keyboard
def get_days_keyboard():
    return ReplyKeyboardMarkup(
        DAYS_KEYBOARD
        , resize_keyboard=True
        , one_time_keyboard=True)


# yes/no keyboard dict
yes_no_keyboard_dict = {
    lang: [[translation_map['YES'][lang]], [translation_map['NO'][lang]]]
    for lang in TRANSLATION_OPTIONS
}


# get the translated yes/no keyboard
def get_yes_no_keyboard_translated(chat_id):
    try:
        return ReplyKeyboardMarkup(yes_no_keyboard_dict[Chat.get(Chat.chat_id == chat_id).language])
    except KeyError:
        return ReplyKeyboardMarkup(yes_no_keyboard_dict['en-us'])  # english keyboard
    except DoesNotExist:
        return 'Please run /start to set language.'
