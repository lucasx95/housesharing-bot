# methods for user related actions and conversation
from _decimal import InvalidOperation

from peewee import IntegrityError, DoesNotExist
from telegram import ForceReply, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from python.code.helper.date_helper import get_month_from_update, get_month_from_args, get_view_reference_month
from python.code.helper.keyboards import get_days_keyboard, get_yes_no_keyboard_translated
from python.code.helper.translator import translate
from python.code.helper.validation import valid_yes_no, valid_day
from python.code.model.entities import Expense, database, Charge
from python.code.model.status import ADD_EXPENSE_NAME, ADD_EXPENSE_VALUE, ADD_EXPENSE_CHARGE_DAY, ADD_EXPENSE_RECURRENT

current_expense = {}


# start add_expense processs
def add_expense_start(bot, update):
    update.message.reply_text(translate('ADD_EXPENSE_NAME', update.message.chat_id),
                              reply_markup=ForceReply())
    return ADD_EXPENSE_NAME


# add expense name
def add_expense_name(bot, update):
    chat_id = update.message.chat_id
    try:
        current_expense[chat_id] = Expense.create(chat_id=chat_id, name=update.message.text)
    except IntegrityError:
        database.rollback()
        update.message.reply_text(translate('ADD_EXPENSE_EXIST', chat_id), reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    update.message.reply_text(translate('ADD_EXPENSE_VALUE', chat_id), reply_markup=ForceReply())
    return ADD_EXPENSE_VALUE


# add expense value
def add_expense_value(bot, update):
    chat_id = update.message.chat_id
    expense = current_expense[chat_id]
    expense.value = update.message.text
    update.message.reply_text(translate('ADD_EXPENSE_CHARGE_DAY', chat_id),
                              reply_markup=get_days_keyboard(),
                              one_time_keyboard=True)
    return ADD_EXPENSE_CHARGE_DAY


# skip expense value
def skip_value(bot, update):
    update.message.reply_text(translate('ADD_EXPENSE_CHARGE_DAY', update.message.chat_id),
                              reply_markup=get_days_keyboard(),
                              one_time_keyboard=True)
    return ADD_EXPENSE_CHARGE_DAY


# add expense value
def add_expense_value_invalid(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text(translate('SET_VALUE_INVALID', chat_id), reply_markup=ForceReply())
    return ADD_EXPENSE_VALUE


# add expense charge_day
def add_expense_charge_day(bot, update):
    chat_id = update.message.chat_id
    expense = current_expense[chat_id]
    expense.charge_day = update.message.text
    expense.paid = False
    update.message.reply_text(translate('ADD_EXPENSE_RECURRENT', chat_id),
                              reply_markup=get_yes_no_keyboard_translated(chat_id),
                              one_time_keyboard=True)
    return ADD_EXPENSE_RECURRENT


# skip expense charge_day
def skip_charge_day(bot, update):
    chat_id = update.message.chat_id
    if not current_expense[chat_id].value:
        update.message.reply_text(translate('ADD_EXPENSE_NONE_VALUE', chat_id))
        return ADD_EXPENSE_CHARGE_DAY
    current_expense[chat_id].paid = True
    update.message.reply_text(translate('ADD_EXPENSE_RECURRENT', chat_id),
                              reply_markup=get_yes_no_keyboard_translated(chat_id),
                              one_time_keyboard=True)
    return ADD_EXPENSE_RECURRENT


# add expense value
def add_expense_charge_day_invalid(bot, update):
    update.message.reply_text(translate('SET_DAY_INVALID', update.message.chat_id),
                              reply_markup=get_days_keyboard(),
                              one_time_keyboard=True)
    return ADD_EXPENSE_VALUE


# add expense recurrent
def add_expense_recurrent(bot, update):
    if not valid_yes_no(update):
        add_expense_recurrent_invalid(update)
    chat_id = update.message.chat_id
    expense = current_expense[chat_id]
    expense.recurrent = (translate('YES', chat_id) == update.message.text)
    try:
        charge = Charge.select().where(Charge.chat_id == chat_id) \
            .order_by(Charge.reference_month.desc()).get()
        expense.charge = charge
    except DoesNotExist:
        update.message.reply_text('Run /start to initiate the bot')

    expense.save()
    current_expense.pop(chat_id)
    update.message.reply_text(translate('FINISHED', chat_id),
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# add expense recurrent invalid
def add_expense_recurrent_invalid(update):
    chat_id = update.message.chat_id
    update.message.reply_text(translate('YES_NO_INVALID', chat_id),
                              reply_markup=get_yes_no_keyboard_translated(chat_id),
                              one_time_keyboard=True)
    return ADD_EXPENSE_RECURRENT


# get all expenses
def get_all_expenses(bot, update):
    chat_id = update.message.chat_id
    expenses = Expense.select(Expense.name).distinct().where(Expense.chat_id == chat_id)
    update.message.reply_text(
        '\n'.join(list(map(lambda exp: exp.name, expenses)))
        if len(expenses) > 0
        else translate('EMPTY_EXPENSES', chat_id))


# late expenses
def late_expenses(bot, update):
    chat_id = update.message.chat_id
    expenses = Expense.select(Expense.name).distinct() \
        .where(Expense.chat_id == chat_id, not Expense.paid,
               Expense.charge.reference_month < get_month_from_update(update) or
               (Expense.charge.reference_month == get_month_from_update(update) and
                Expense.charge_day < update.message.date.day))
    update.message.reply_text(
        '\n'.join(list(
            map(lambda exp: exp.name + translate('OF_BETWEEN', chat_id) + get_view_reference_month(
                exp.charge.reference_month),
                expenses)))
        if len(expenses) > 0
        else translate('EMPTY_EXPENSES_UNPAID', chat_id))


# enable recurrence for expense
def enable_recurrence(bot, update, args):
    chat_id = update.message.chat_id
    name = args[0]
    try:
        expense = Expense.get(Expense.chat_id == chat_id, Expense.name == name,
                              Expense.charge == Charge.get(Charge.chat_id == chat_id,
                                                           Charge.reference_month == get_month_from_update(update)))
        expense.recurrent = True
        expense.save()
        reply_text = translate('EDIT_EXPENSE_SUCCESS', chat_id)
    except DoesNotExist:
        reply_text = translate('EDIT_EXPENSE_ERROR', chat_id)
    update.message.reply_text(reply_text)


# disable recurrence for expense
def disable_recurrence(bot, update, args):
    chat_id = update.message.chat_id
    name = args[0]
    try:
        expense = Expense.get(Expense.chat_id == chat_id, Expense.name == name,
                              Expense.charge == Charge.get(Charge.chat_id == chat_id,
                                                           Charge.reference_month == get_month_from_update(update)))
        expense.recurrent = False
        expense.save()
        reply_text = translate('EDIT_EXPENSE_SUCCESS', chat_id)
    except DoesNotExist:
        reply_text = translate('EDIT_EXPENSE_ERROR', chat_id)
    update.message.reply_text(reply_text)


# change value recurrence for expense
def edit_expense_value(bot, update, args):
    chat_id = update.message.chat_id
    name, value = args[:2]
    reference_month = get_month_from_args(args, 2, update)
    try:
        expense = Expense.get(Expense.chat_id == chat_id, Expense.name == name,
                              Expense.charge == Charge.get(Charge.chat_id == chat_id,
                                                           Charge.reference_month == reference_month))
        expense.value = value
        expense.save()
        reply_text = translate('EDIT_EXPENSE_SUCCESS', chat_id)
    except DoesNotExist:
        reply_text = translate('EDIT_EXPENSE_ERROR', chat_id)
    except InvalidOperation:
        reply_text = translate('INVALID_PARAMETER', update.message.chat_id)
    update.message.reply_text(reply_text)


# change charge_day for expense
def edit_expense_charge_day(bot, update, args):
    chat_id = update.message.chat_id
    name, day = args[0:2]
    reference_month = get_month_from_args(args, 2, update)
    if not valid_day(day):
        reply_text = translate('INVALID_PARAMETER', update.message.chat_id)
    else:
        try:
            expense = Expense.get(Expense.chat_id == chat_id, Expense.name == name,
                                  Expense.charge == Charge.get(Charge.chat_id == chat_id,
                                                               Charge.reference_month == reference_month))
            expense.day = day
            expense.save()
            reply_text = translate('EDIT_EXPENSE_SUCCESS', chat_id)
        except DoesNotExist:
            reply_text = translate('EDIT_EXPENSE_ERROR', chat_id)
    update.message.reply_text(reply_text)


# pay expense
def pay_expense(bot, update, args):
    chat_id = update.message.chat_id
    name = args[0]
    reference_month = get_month_from_args(args, 1, update)
    try:
        expense = Expense.get(Expense.chat_id == chat_id, Expense.name == name,
                              Expense.charge == Charge.get(Charge.chat_id == chat_id,
                                                           Charge.reference_month == reference_month))
        if expense.value:
            expense.paid = True
            expense.save()
            reply_text = translate('EDIT_EXPENSE_SUCCESS', chat_id)
        else:
            reply_text = translate('PAY_WITHOUT_VALUE', chat_id)
    except DoesNotExist:
        reply_text = translate('EDIT_EXPENSE_ERROR', chat_id)
    update.message.reply_text(reply_text)


# delete expense
def delete_expense(bot, update, args):
    chat_id = update.message.chat_id
    name = args[0]
    try:
        expense = Expense.get(Expense.chat_id == chat_id, Expense.name == name,
                              Expense.charge == Charge.get(Charge.chat_id == chat_id,
                                                           Charge.reference_month == get_month_from_update(update)))
        expense.delete_instance()
        reply_text = translate('DELETE_EXPENSE', chat_id)
    except DoesNotExist:
        reply_text = translate('EDIT_EXPENSE_ERROR', chat_id)
    update.message.reply_text(reply_text)


# cancel add expense
def cancel_expense(bot, update):
    chat_id = update.message.chat_id
    expense = current_expense.pop(chat_id, None)
    if expense:
        expense.delete_instance()
    update.message.reply_text(translate('CANCEL', update.message.chat_id))
    return ConversationHandler.END
