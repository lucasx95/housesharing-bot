from telegram import ReplyKeyboardMarkup

from python.code.helper.translator import TRANSLATION_OPTIONS, translate, translation_map

# get supported languages keyboard
from python.code.model.entities import Chat, DoesNotExist

LANGUAGES_KEYBOARD = ReplyKeyboardMarkup(list(map(lambda lang: [lang], TRANSLATION_OPTIONS))
                                         , one_time_keyboard=True)
# get days keyboard
DAYS_KEYBOARD = ReplyKeyboardMarkup(
    [map(str, range(1, 10)), map(str, range(11, 20)), map(str, range(21, 30)), ['31'] + ['  '] * 9]
    , resize_keyboard=True)

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
