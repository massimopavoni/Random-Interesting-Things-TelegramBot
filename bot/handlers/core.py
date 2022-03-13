from json import load as json_load

from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext import Dispatcher, CallbackContext

with open('bot/handlers/core_config.json', 'r', encoding='utf-8') as f:
    core_config = json_load(f)


def init(dispatcher: Dispatcher, admin_user_filter):
    dispatcher.add_handler(CommandHandler('start', start, filters=admin_user_filter))


def start(update: Update, context: CallbackContext):
    update.effective_message.reply_text(text=core_config['start_message'])
