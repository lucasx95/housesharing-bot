# methods for charge related actions and conversations
from functools import reduce

from python.code.helper.date_helper import get_month_from_args, get_month_from_update
from python.code.helper.translator import translate
from python.code.model.entities import Charge, User


# get string with user.name - month value for all users in charge
def get_month_values(charge, update):
    users = User.select().where(User.active, User.chat_id == update.message.chat_id) \
        if charge.reference_month == get_month_from_update(update) and charge.charge_day > update.message.date.day else \
        charge.users
    expenses_value = reduce(lambda x, y: x.value + y.value, charge.expenses).value / users.count()
    return '\n'.join(
        list(map(lambda user: user.name + ' - ' + str(user.base_value + expenses_value), users)))


# get the value of monthly fee for a given reference_month
def get_charge_individual_value(bot, update, args):
    reference_month = get_month_from_args(args, 0, update)
    chat_id = update.message.chat_id
    charge = Charge.select(). \
        where(Charge.chat_id == chat_id, Charge.reference_month == reference_month).get()
    # check if there's expenses withou values set
    unvalued_expenses = list(filter(lambda exp: exp.value is None, charge.expenses))
    reply_text = translate('CHARGE_VALUES_HEADER', chat_id) + get_month_values(charge, update) \
        if len(unvalued_expenses) == 0 else \
        translate('CHARGE_EXPENSES_WITHOUT_VALUE_HEADER', chat_id) \
        + '\n'.join(list(map(lambda exp: exp.name, unvalued_expenses)))
    update.message.reply_text(reply_text)
