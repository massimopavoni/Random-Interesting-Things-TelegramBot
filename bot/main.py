import os
import glob
from importlib import import_module

from telegram.ext import Updater, Filters

token = os.getenv('TELEGRAM_BOT_TOKEN')
admin_user_filter = Filters.user(user_id=int(os.getenv('TELEGRAM_ADMIN_USER_ID')))


def load_handlers(dispatcher):
    for file_name in glob.glob('bot/handlers/*.py'):
        handler_module, _ = os.path.splitext(file_name.split('/')[-1])
        module = import_module(f'.{handler_module}', 'handlers')
        module.init(dispatcher, admin_user_filter)


if __name__ == '__main__':
    updater = Updater(token=token, use_context=True)
    load_handlers(updater.dispatcher)
    updater.start_polling()
