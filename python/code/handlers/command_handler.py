# handlers dict method
from telegram.ext import *

from python.code.handlers.chat_handler import *
from python.code.handlers.expense_handler import *
from python.code.handlers.user_handler import *
from python.code.helper.translator import TRANSLATION_OPTIONS_REGEX
from python.code.model.status import *

# Define the handlers dict
handlers = {
    # start handler
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
    # user handlers
    'add_user': ConversationHandler(
        entry_points=[CommandHandler('add_user', add_user_start)],

        states={
            ADD_USER_NAME: [MessageHandler(Filters.all, add_user_name)],

            ADD_USER_BASE_VALUE: [RegexHandler('^[0-9]+(\.[0-9]+)?', add_user_base_value),
                                  MessageHandler(Filters.text, add_user_base_value_invalid)]
        },

        fallbacks=[CommandHandler('cancel', cancel_user)]
    ),
    'edit_user_name': CommandHandler('edit_user_name', edit_user_name, pass_args=True),
    'edit_user_base': CommandHandler('edit_user_base', edit_user_base_value, pass_args=True),
    'activate_user': CommandHandler('activate_user', activate_user, pass_args=True),
    'deactivate_user': CommandHandler('deactivate_user', deactivate_user, pass_args=True),
    'get_users': CommandHandler('get_users', get_users),
    # expenses handlers
    'add_expense': ConversationHandler(
        entry_points=[CommandHandler('add_expense', add_expense_start)],
        states={
            ADD_EXPENSE_NAME: [MessageHandler(Filters.text, add_expense_name)],
            ADD_EXPENSE_VALUE: [RegexHandler('^[0-9]+(\.[0-9]+)?', add_expense_value),
                                CommandHandler('skip', skip_value),
                                MessageHandler(Filters.text, add_expense_value_invalid)],
            ADD_EXPENSE_CHARGE_DAY: [RegexHandler('^((0?[1-9])|[1-2][0-9]|3[0-1])', add_expense_charge_day),
                                     CommandHandler('skip', skip_charge_day),
                                     MessageHandler(Filters.all, add_expense_charge_day_invalid)],
            ADD_EXPENSE_RECURRENT: [MessageHandler(Filters.all, add_expense_recurrent)]
        },
        fallbacks=[CommandHandler('cancel', cancel_expense)]
    ),
    'get_expenses': CommandHandler('get_expenses', get_all_expenses),
    'enable_recurrence': CommandHandler('enable_recurrence', enable_recurrence, pass_args=True),
    'disable_recurrence': CommandHandler('disable_recurrence', disable_recurrence, pass_args=True),
    'delete_expense': CommandHandler('delete_expense', delete_expense, pass_args=True),
    'edit_expense_value': CommandHandler('edit_expense_value', edit_expense_value, pass_args=True),
    'edit_expense_day': CommandHandler('edit_expense_day', edit_expense_charge_day, pass_args=True),
    'pay_expense': CommandHandler('pay_expense', pay_expense, pass_args=True)

}
