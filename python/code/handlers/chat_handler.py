# methods for chat related actions and conversations
import logging

from peewee import DoesNotExist
from telegram import ReplyKeyboardRemove
from telegram.error import TimedOut, NetworkError, ChatMigrated, TelegramError, Unauthorized
from telegram.ext import ConversationHandler

from python.code.helper.date_helper import get_month_from_update
from python.code.helper.keyboards import get_languages_keyboard, get_days_keyboard
from python.code.helper.translator import translate
from python.code.model.entities import Chat, Charge
from python.code.model.status import SET_CHAT_LANGUAGE, SET_CHARGE_DAY

# enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# start the bot by asking the language
def start(bot, update):
    update.message.reply_text(
        'What language do you want?',
        reply_markup=get_languages_keyboard())
    return SET_CHAT_LANGUAGE


# set the language and ask for the charge_day
def set_chat_language(bot, update):
    try:
        chat = Chat.get(Chat.chat_id == update.message.chat_id)
        chat.language = update.message.text
        chat.save()
    except DoesNotExist:
        Chat.create(chat_id=update.message.chat_id, language=update.message.text)
    update.message.reply_text(translate('SET_CHARGE_DAY', update.message.chat_id),
                              reply_markup=get_days_keyboard(),
                              one_time_keyboard=True)
    return SET_CHARGE_DAY


# in case the response for language is not valid
def set_chat_language_invalid(bot, update):
    update.message.reply_text(translate('SET_CHAT_LANGUAGE_INVALID', update.message.chat_id),
                              reply_markup=get_languages_keyboard())
    return SET_CHAT_LANGUAGE


# set the charge day
def set_charge_day(bot, update):
    reference_month = get_month_from_update(update)
    try:
        charge = Charge. \
            get(Charge.chat_id == update.message.chat_id, Charge.reference_month == reference_month)
        charge.charge_day = update.message.text
        charge.save()
    except DoesNotExist:
        Charge.create(chat_id=update.message.chat_id, reference_month=reference_month, charge_day=update.message.text)
    update.message.reply_text(translate('WELCOME_MESSAGE', update.message.chat_id),
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# in case of invalid date
def set_charge_day_invalid(bot, update):
    update.message.reply_text(translate('SET_DAY_INVALID', update.message.chat_id),
                              reply_markup=get_days_keyboard())
    return SET_CHARGE_DAY


# cancel the conversation
def cancel(bot, update):
    update.message.reply_text(translate('CANCEL', update.message.chat_id))
    return ConversationHandler.END


# cancel without conversation
def cancel_none(bot, update):
    update.message.reply_text(translate('CANCEL_NONE', update.message.chat_id))


# parameter invalid
def parameter_invalid(bot, update):
    update.message.reply_text(translate('INVALID_PARAMETER', update.message.chat_id))


# print on console errors
def error(bot, update, error):
    chat_id = update.message.chat_id
    try:
        raise error
    # remove chat from db
    except Unauthorized:
        try:
            chat = Chat.get(Chat.chat_id == chat_id)
            chat.delete_instance()
        except DoesNotExist:
            logger.warning('Update "%s" caused error "%s"' % (update, error))
    # for network problems answer CONNECTION_ERROR
    except (TimedOut, NetworkError):
        update.message.reply_text(translate('CONNECTION_ERROR', chat_id))
    # if chat_id migrated update database
    except ChatMigrated as e:
        chat = Chat.get(Chat.chat_id == chat_id)
        chat.chat_id = e.new_chat_id
        chat.save()
    # in case of other error UNEXPECTED_ERROR and log
    except TelegramError:
        update.message.reply_text(translate('UNEXPECTED_ERROR', chat_id))
        logger.warning('Update "%s" caused error "%s"' % (update, error))
