from python.code.helper.keyboards import get_yes_no_keyboard_translated


# valid if is yes or no from keyboard
def valid_yes_no(update):
    return [update.message.text] in get_yes_no_keyboard_translated(update.message.chat_id).keyboard


# valid if is a day
def valid_day(day):
    try:
        return int(day) in range(1, 32)
    except ValueError:
        return False
