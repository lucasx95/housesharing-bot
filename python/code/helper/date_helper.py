# helper for date and time
def get_month_from_update(update):
    return str(update.message.date.year) + str(update.message.date.month).zfill(2)


# get reference_month from args
def get_month_from_args(month, pos, update):
    return month[pos][3:7] + month[pos][0:2] if len(month) > pos else get_month_from_update(update)


# get month formatted for view
def get_view_reference_month(month):
    return month[4:6] + '/' + month[0:4]
