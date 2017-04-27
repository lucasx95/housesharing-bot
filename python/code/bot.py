# telegram bot configuration and run
from pathlib import Path
from python.code.handlers.chat_handler import error
from python.code.handlers.command_handler import handlers, Updater
from python.resources.properties import api_key

# init the updater
updater = Updater(api_key)

# get the commands
with open(str(Path().resolve()) + '/bot/commands') as commands_file:
    commands = list(map(lambda cmd: cmd.split(' - ')[0], commands_file.readlines()))

# add the handlers
for command in commands:
    updater.dispatcher.add_handler(handlers[command])

# log all errors
updater.dispatcher.add_error_handler(error)

# start de updater
updater.start_polling()
updater.idle()
