# handlers dict method
from telegram.ext import *
from python.code.handlers.chat_handler import *
from python.code.handlers.user_handler import *
from python.code.model.status import *
from python.resources.translator import TRANSLATION_OPTIONS_REGEX

# Define the handlers dict
handlers = {
    'start': ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SET_CHAT_LANGUAGE: [RegexHandler(TRANSLATION_OPTIONS_REGEX, set_chat_language),
                                MessageHandler(Filters.all, set_chat_language_invalid)],

            SET_CHARGE_DAY: [RegexHandler('^((0?[1-9])|[1-2][0-9]|3[0-1])', set_charge_day),
                             MessageHandler(Filters.all, set_charge_day_invalid)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    ),
    'add_user': ConversationHandler(
        entry_points=[CommandHandler('add_user', add_user_start)],

        states={
            ADD_USER_NAME: [MessageHandler(Filters.all, add_user_name)],

            ADD_USER_BASE_VALUE: [RegexHandler('^[0-9]+(\.[0-9]+)?', add_user_base_value),
                                  MessageHandler(Filters.text, add_user_base_value_invalid)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    ),
    'edt_user_name': CommandHandler('edt_user_name', edit_user_name, pass_args=True),
    'edt_user_base': CommandHandler('edt_user_base', edit_user_base_value, pass_args=True),
    'activate_user': CommandHandler('activate_user', activate_user, pass_args=True),
    'deactivate_user': CommandHandler('deactivate_user', deactivate_user, pass_args=True),
    'get_users': CommandHandler('get_users', get_users)

}
