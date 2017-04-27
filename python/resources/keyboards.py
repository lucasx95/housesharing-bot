from telegram import ReplyKeyboardMarkup
from python.resources.translator import TRANSLATION_OPTIONS

# get supported languages keyboard
LANGUAGES_KEYBOARD = ReplyKeyboardMarkup(list(map(lambda lang: [lang], TRANSLATION_OPTIONS)), one_time_keyboard=True)
# get days keyboard
DAYS_KEYBOARD = ReplyKeyboardMarkup(
    [map(str, range(1, 10)), map(str, range(11, 20)), map(str, range(21, 30)), ['31'] + ['  '] * 9],
    one_time_keyboard=True,
    resize_keyboard=True)
