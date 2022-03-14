from json import load as json_load
from os import getenv as os_getenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Dispatcher, JobQueue

with open('bot/handlers/post_config.json', 'r', encoding='utf-8') as f:
    post_config = json_load(f)

post_keyboard = [
    [InlineKeyboardButton(post_config['list_posts_button'], callback_data='post_list')],
    [InlineKeyboardButton(post_config['new_post_button'], callback_data='post_new')]
]

list_keyboard = [
    InlineKeyboardButton(post_config['back_to_post_button'], callback_data='post_back_to_post')
]

view_additional_keyboard = [
    InlineKeyboardButton(post_config['view_post_button'], callback_data='view')
]

publish_schedule_additional_keyboard = [
    InlineKeyboardButton(post_config['publish_post_button'], callback_data='publish'),
    InlineKeyboardButton(post_config['schedule_post_button'], callback_data='schedule')
]

edit_delete_additional_keyboard = [
    InlineKeyboardButton(post_config['edit_post_button'], callback_data='edit'),
    InlineKeyboardButton(post_config['delete_post_button'], callback_data='delete')
]

telegram_channel_id = os_getenv('TELEGRAM_CHANNEL_ID')
updater_job_queue: JobQueue


def init(dispatcher: Dispatcher, admin_user_filter, job_queue):
    global updater_job_queue
    updater_job_queue = job_queue
    dispatcher.add_handler(CommandHandler('post', post, filters=admin_user_filter))
    dispatcher.add_handler(CallbackQueryHandler(post_buttons, pattern='^post_'))


def post(update: Update, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup(post_keyboard)
    if update.message:
        update.effective_message.reply_text(post_config['post_message'], reply_markup=reply_markup)
    else:
        update.effective_message.edit_text(post_config['post_message'], reply_markup=reply_markup)


def post_buttons(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    match query.data.replace('post_', ''):
        case 'list':
            list_posts(update, context)
        case 'new':
            update.effective_message.reply_text('trolol')
        case 'back_to_post':
            post(update, context)


def list_posts(update: Update, context: CallbackContext) -> None:
    message = '\n'.join([job.name for job in updater_job_queue.jobs()])
    if message:
        keyboard = [
            view_additional_keyboard,
            publish_schedule_additional_keyboard,
            edit_delete_additional_keyboard,
            list_keyboard
        ]
    else:
        keyboard = [list_keyboard]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.edit_text(message if message else post_config['no_posts_message'],
                                       reply_markup=reply_markup)
