from datetime import datetime, time
from io import BytesIO
from json import load as json_load
from os import getenv as os_getenv, path as os_path

from pytz import utc
from telegram import Update, ParseMode
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    Dispatcher,
    MessageHandler
)
from telegram.utils.helpers import escape_markdown
from tinydb import TinyDB

posts_db = 'bot/db/posts.json'

with open('bot/handlers/post_config.json', 'r', encoding='utf-8') as f:
    post_config = json_load(f)

telegram_channel_id = os_getenv('TELEGRAM_CHANNEL_ID')

current_post_data = {}


def init(dispatcher: Dispatcher, admin_user_filter):
    dispatcher.add_handler(CommandHandler('list', list_posts, filters=admin_user_filter))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('post', new_post, filters=admin_user_filter)],
        states={TITLE: [MessageHandler(Filters.text, post_title)],
                CREDIT: [MessageHandler(Filters.text, post_credit)],
                IMAGE: [MessageHandler(Filters.photo, post_image)],
                LINKS: [MessageHandler(Filters.text, post_links)],
                BRIEF: [MessageHandler(Filters.text, post_brief)],
                TAGS: [MessageHandler(Filters.text, post_tags)],
                SCHEDULE: [MessageHandler(Filters.text, post_schedule)]},
        fallbacks=[CommandHandler('cancel', cancel, filters=admin_user_filter)]))
    target_time = time(hour=16, minute=32, second=48, tzinfo=utc)
    dispatcher.job_queue.run_daily(post_to_channel, target_time, days=(0, 1, 2, 3, 4, 5, 6))


TITLE, CREDIT, IMAGE, LINKS, BRIEF, TAGS, SCHEDULE = range(7)


def list_posts(update: Update, context: CallbackContext):
    message = escape_markdown(post_config['no_posts_message'], version=2)
    if os_path.exists(posts_db):
        db = TinyDB(posts_db)
        posts = db.all()
        db.close()
        if len(posts) > 0:
            message = f"{escape_markdown(post_config['list_posts_message'], version=2)}\n\n" + \
                      '\n'.join([f"*{escape_markdown(post['title'], version=2)}* "
                                 f"by _{escape_markdown(post['credit'], version=2)}_ "
                                 f"on {escape_markdown(post['schedule'], version=2)}" for post in posts])
    update.effective_message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)


def new_post(update: Update, context: CallbackContext):
    global current_post_data
    current_post_data.clear()
    update.effective_message.reply_text(post_config['new_post_message'])
    update.effective_message.reply_text(post_config['new_post_title_message'])
    return TITLE


def cancel(update: Update, context: CallbackContext):
    update.effective_message.reply_text(post_config['new_post_cancelled_message'])
    current_post_data.clear()
    return ConversationHandler.END


def post_title(update: Update, context: CallbackContext):
    global current_post_data
    current_post_data['title'] = update.message.text
    update.effective_message.reply_text(post_config['new_post_credit_message'])
    return CREDIT


def post_credit(update: Update, context: CallbackContext):
    global current_post_data
    current_post_data['credit'] = update.message.text
    update.effective_message.reply_text(post_config['new_post_image_message'])
    return IMAGE


def post_image(update: Update, context: CallbackContext):
    global current_post_data
    current_post_data['image'] = update.message.photo[-1].get_file().download_as_bytearray().hex()
    update.effective_message.reply_text(post_config['new_post_links_message'])
    return LINKS


def post_links(update: Update, context: CallbackContext):
    global current_post_data
    current_post_data['links'] = {}
    links = update.message.text.split(',')
    for link in links:
        link_args = link.split(' is ')
        current_post_data['links'].update({link_args[0]: link_args[1]} if len(link_args) == 2 else {link_args[0]: ''})
    update.effective_message.reply_text(post_config['new_post_brief_message'])
    return BRIEF


def post_brief(update: Update, context: CallbackContext):
    global current_post_data
    current_post_data['brief'] = update.message.text
    update.effective_message.reply_text(post_config['new_post_tags_message'])
    return TAGS


def post_tags(update: Update, context: CallbackContext):
    global current_post_data
    current_post_data['tags'] = update.message.text.split(',')
    update.effective_message.reply_text(post_config['new_post_schedule_message'])
    return SCHEDULE


def post_schedule(update: Update, context: CallbackContext):
    global current_post_data
    current_post_data['schedule'] = update.message.text
    if not os_path.exists(posts_db):
        open(posts_db, 'w').close()
    db = TinyDB(posts_db)
    db.insert(current_post_data)
    db.close()
    update.effective_message.reply_text(post_config['new_post_saved_message'])
    current_post_data.clear()
    return ConversationHandler.END


def post_to_channel(context: CallbackContext):
    db = TinyDB(posts_db)
    utc_now = datetime.utcnow().strftime('%Y-%m-%d')
    post_data = db.search(lambda p: p['schedule'] == utc_now)
    db.remove(lambda p: p['schedule'] == utc_now)
    db.close()
    if len(post_data) > 0:
        for post in post_data:
            links = '\n'.join(f"{v}: {k}" if v else k for (k, v) in post['links'].items())
            tags = ' '.join(f"#{t}" for t in post['tags'])
            context.bot.send_photo(chat_id=telegram_channel_id,
                                   photo=BytesIO(bytes.fromhex(post['image'])),
                                   caption=f"*{escape_markdown(post['title'], version=2)}*\n"
                                           f"by _{escape_markdown(post['credit'])}_\n\n"
                                           f"{escape_markdown(links, version=2)}\n\n"
                                           f"{escape_markdown(post['brief'], version=2)}\n\n"
                                           f"{escape_markdown(tags, version=2)}",
                                   parse_mode=ParseMode.MARKDOWN_V2)
