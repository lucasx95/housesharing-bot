# helper for date and time
def get_month_from_update(update):
    return str(update.message.date.month).zfill(2) + '/' + str(update.message.date.year)
