import os
from importlib import import_module

from telegram.ext import Updater, Filters

token = os.getenv('TELEGRAM_BOT_TOKEN')
admin_user_filter = Filters.user(user_id=int(os.getenv('TELEGRAM_ADMIN_USER_ID')))


def load_handlers(dispatcher):
    module = import_module(f'.post', 'handlers')
    module.init(dispatcher, admin_user_filter, updater.job_queue)
    module = import_module(f'.core', 'handlers')
    module.init(dispatcher, admin_user_filter)


if __name__ == '__main__':
    updater = Updater(token=token, use_context=True)
    load_handlers(updater.dispatcher)
    updater.start_polling()
