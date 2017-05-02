# methods for user related actions and conversation
from _decimal import InvalidOperation

from peewee import IntegrityError, DoesNotExist
from telegram import ForceReply, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from python.code.helper.translator import translate
from python.code.model.entities import User, database
from python.code.model.status import ADD_USER_NAME, ADD_USER_BASE_VALUE

current_user = {}


# start add_user processs
def add_user_start(bot, update):
    update.message.reply_text(translate('ADD_USER_NAME', update.message.chat_id),
                              reply_markup=ForceReply())
    return ADD_USER_NAME


# add user name
def add_user_name(bot, update):
    chat_id = update.message.chat_id
    try:
        current_user[chat_id] = User.create(chat_id=chat_id, name=update.message.text, active=True)
    except IntegrityError:
        database.rollback()
        update.message.reply_text(translate('ADD_USER_EXIST', chat_id), reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    update.message.reply_text(translate('ADD_USER_BASE_VALUE', chat_id), reply_markup=ForceReply())
    return ADD_USER_BASE_VALUE


# add user base_value
def add_user_base_value(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text(translate('FINISHED', chat_id), reply_markup=ReplyKeyboardRemove())
    user = current_user[chat_id]
    user.base_value = update.message.text
    user.save()
    current_user.pop(chat_id)
    return ConversationHandler.END


# add user base_value invalid
def add_user_base_value_invalid(bot, update):
    update.message.reply_text(translate('SET_VALUE_INVALID', update.message.chat_id),
                              reply_markup=ForceReply())
    return ADD_USER_BASE_VALUE


# edit user name
def edit_user_name(bot, update, args):
    name, new_name = args
    try:
        user = User.get(User.chat_id == update.message.chat_id, User.name == name)
        user.name = new_name
        user.save()
        reply_text = translate('EDT_USER_SUCCESS', update.message.chat_id)
    except DoesNotExist:
        reply_text = translate('EDT_USER_NON_EXIST', update.message.chat_id)
    update.message.reply_text(reply_text)


# edit user base_value
def edit_user_base_value(bot, update, args):
    name, base_value = args
    try:
        user = User.get(User.chat_id == update.message.chat_id, User.name == name)
        user.base_value = base_value
        user.save()
        reply_text = translate('EDT_USER_SUCCESS', update.message.chat_id)
    except DoesNotExist:
        reply_text = translate('EDT_USER_NON_EXIST', update.message.chat_id)
    except InvalidOperation:
        reply_text = translate('INVALID_PARAMETER', update.message.chat_id)
    update.message.reply_text(reply_text)


# activates user name
def activate_user(bot, update, args):
    name = args[0]
    try:
        user = User.get(User.chat_id == update.message.chat_id, User.name == name)
        user.active = True
        user.save()
        reply_text = translate('EDT_USER_SUCCESS', update.message.chat_id)
    except DoesNotExist:
        reply_text = translate('EDT_USER_NON_EXIST', update.message.chat_id)
    update.message.reply_text(reply_text)


# deactivates user name
def deactivate_user(bot, update, args):
    name = args[0]
    try:
        user = User.get(User.chat_id == update.message.chat_id, User.name == name)
        user.active = False
        user.save()
        reply_text = translate('EDT_USER_SUCCESS', update.message.chat_id)
    except DoesNotExist:
        reply_text = translate('EDT_USER_NON_EXIST', update.message.chat_id)
    update.message.reply_text(reply_text)


# get users
def get_users(bot, update):
    query = User.select().where(User.chat_id == update.message.chat_id, User.active)
    update.message.reply_text(
        'Nome - Valor Base\n' +
        '\n'.join(
            map(lambda user: user.name + ' - ' + str(user.base_value), query))
        if query.count() > 0
        else translate('ZERO_USERS', update.message.chat_id))


# cancel user
def cancel_user(bot, update):
    chat_id = update.message.chat_id
    user = current_user.pop(chat_id, None)
    if user:
        user.delete_instance()
    update.message.reply_text(translate('CANCEL', update.message.chat_id))
    return ConversationHandler.END
